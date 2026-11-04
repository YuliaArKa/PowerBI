const fs = require('node:fs');
const path = require('node:path');
const pq = require('@microsoft/powerquery-parser');

async function main() {
  const root = path.resolve(__dirname, '../..');
  const models = fs.readdirSync(root).filter(n => n.endsWith('.SemanticModel'));
  if (models.length !== 1) throw new Error('Expected exactly one semantic model.');
  const definition = path.join(root, models[0], 'definition');
  const queries = [];
  for (const filename of fs.readdirSync(path.join(definition, 'tables'))) {
    const text = fs.readFileSync(path.join(definition, 'tables', filename), 'utf8');
    if (!/^\tpartition .* = m$/m.test(text)) continue;
    const source = text.split('\t\tsource =\n')[1];
    if (!source) throw new Error(`Missing M source: ${filename}`);
    const lines = [];
    for (const line of source.split('\n')) {
      if (!line.startsWith('\t\t\t') && line.trim()) break;
      lines.push(line.startsWith('\t\t\t') ? line.slice(3) : line);
    }
    queries.push([filename, lines.join('\n')]);
  }
  const parameter = fs.readFileSync(path.join(definition, 'expressions.tmdl'), 'utf8')
    .split('\n')[0].replace(/^expression DataFolder = /, '');
  queries.push(['DataFolder', parameter]);
  let errors = 0;
  for (const [name, source] of queries) {
    const result = await pq.TaskUtils.tryLexParse(pq.DefaultSettings, source);
    console.log(`${name}: ${result.resultKind}`);
    if (result.resultKind !== 'Ok') {
      console.error(JSON.stringify(result.error));
      errors++;
    }
  }
  if (queries.length === 0 || errors) process.exitCode = 1;
}

main().catch(e => { console.error(e); process.exitCode = 1; });
