using Microsoft.AnalysisServices.Tabular;

if (args.Length != 1) {
    Console.Error.WriteLine("Usage: TmdlValidator <SemanticModel/definition>");
    return 2;
}
try {
    var database = TmdlSerializer.DeserializeDatabaseFromFolder(args[0]);
    var m = database.Model;
    Console.WriteLine(System.Text.Json.JsonSerializer.Serialize(new {
        tables=m.Tables.Count, relationships=m.Relationships.Count,
        measures=m.Tables.Sum(t=>t.Measures.Count), expressions=m.Expressions.Count
    }));
    return 0;
} catch(Exception e) {
    Console.Error.WriteLine(e.ToString());
    return 1;
}
