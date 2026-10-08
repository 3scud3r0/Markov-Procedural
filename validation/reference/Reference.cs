using System;
using System.IO;
using System.Linq;
using System.Text.Json;
using System.Xml.Linq;
using System.Collections.Generic;
class Reference {
static void Main(string[] args) {
if(args[0]=="rng") {
var seeds=new List<int> {0,1,-1,42,12345,161803398,161803399,1800000000,1923919228,2147483647,-2147483648};
var meta=new Random(77);for(int i=0;i<100;i++) seeds.Add(meta.Next());
var records=seeds.Select(seed=> {var r=new Random(seed);return new {seed,values=Enumerable.Range(0,128).Select(i=>r.Next()).ToArray()};});
File.WriteAllText(args[1],JsonSerializer.Serialize(records));return;
}
string basepath=args[0]; Directory.SetCurrentDirectory(basepath);
var cases=JsonDocument.Parse(File.ReadAllText(args[1])).RootElement;
string output=args[2]; Directory.CreateDirectory(output);
var palette=XDocument.Load("resources/palette.xml").Root.Elements("color").ToDictionary(x=>x.Get<char>("symbol"),x=>unchecked((int)0xff000000)|Convert.ToInt32(x.Get<string>("value"),16));
foreach(var c in cases.EnumerateArray()) {
string id=c.GetProperty("id").GetString(),name=c.GetProperty("model").GetString();
try {
int mx=c.GetProperty("mx").GetInt32(),my=c.GetProperty("my").GetInt32(),mz=c.GetProperty("mz").GetInt32(),seed=c.GetProperty("seed").GetInt32(),steps=c.GetProperty("steps").GetInt32();
string modelPath=c.TryGetProperty("fixture",out var fixture) && fixture.GetBoolean() ? Path.GetFullPath(Path.Combine(basepath,"..","validation","fixtures",name+".xml")) : $"models/{name}.xml";
var ip=Interpreter.Load(XDocument.Load(modelPath,LoadOptions.SetLineInfo).Root,mx,my,mz);
if(ip==null)throw new Exception("Interpreter.Load returned null");
var last=ip.Run(seed,steps,false).Last();
File.WriteAllBytes(Path.Combine(output,id+".state"),last.Item1);
int[] colors=last.Item2.Select(ch=>palette[ch]).ToArray();
int margin=c.TryGetProperty("margin",out var mg)?mg.GetInt32():0;
var (pixels,w,h)=Graphics.Render(last.Item1,last.Item3,last.Item4,last.Item5,colors,c.GetProperty("pixelsize").GetInt32(),margin);
if(margin>0)GUI.Draw(name,ip.root,ip.current,pixels,w,h,palette);
Graphics.SaveBitmap(pixels,w,h,Path.Combine(output,id+".png"));
if(last.Item5>1 && last.Item3<256 && last.Item4<256 && last.Item5<256)VoxHelper.SaveVox(last.Item1,(byte)last.Item3,(byte)last.Item4,(byte)last.Item5,colors,Path.Combine(output,id+".vox"));
File.WriteAllText(Path.Combine(output,id+".json"),JsonSerializer.Serialize(new {mx=last.Item3,my=last.Item4,mz=last.Item5,counter=ip.counter,legend=new string(last.Item2)}));
Console.WriteLine("CASE "+id+" OK");
} catch(Exception ex) {File.WriteAllText(Path.Combine(output,id+".error"),ex.ToString());Console.WriteLine("CASE "+id+" ERROR "+ex.Message);}
}
}
}
