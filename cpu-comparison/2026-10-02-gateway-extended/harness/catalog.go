package main
import("encoding/json";"os";"sort";"fmt";"strings";"sigs.k8s.io/gateway-api/pkg/features";"sigs.k8s.io/gateway-api/conformance/tests")
func main(){
 mesh:=features.SetsToNamesSet(features.MeshCoreFeatures,features.MeshExtendedFeatures)
 fs:=[]features.Feature{}; names:=[]string{}
 for f:=range features.AllFeatures {if !mesh.Has(f.Name){fs=append(fs,f);names=append(names,string(f.Name))}}
 sort.Slice(fs,func(i,j int)bool{return fs[i].Name<fs[j].Name});sort.Strings(names)
 ts:=[]map[string]any{}
 for _,t:=range tests.ConformanceTests {selected:=true;for _,f:=range t.Features{if !features.SetsToNamesSet(features.AllFeatures).Has(f) || mesh.Has(f){selected=false}};ts=append(ts,map[string]any{"name":t.ShortName,"features":t.Features,"provisional":t.Provisional,"selected":selected})}
 sort.Slice(ts,func(i,j int)bool{return ts[i]["name"].(string)<ts[j]["name"].(string)})
 e:=json.NewEncoder(os.Stdout);e.SetIndent("","  ");e.Encode(map[string]any{"features":fs,"tests":ts});fmt.Fprintln(os.Stderr,strings.Join(names,","))
}
