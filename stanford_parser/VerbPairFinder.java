import java.io.*;
import java.util.*;
import edu.stanford.nlp.process.Tokenizer;
import edu.stanford.nlp.process.TokenizerFactory;
import edu.stanford.nlp.process.CoreLabelTokenFactory;
import edu.stanford.nlp.process.DocumentPreprocessor;
import edu.stanford.nlp.process.PTBTokenizer;
import edu.stanford.nlp.ling.CoreLabel;
import edu.stanford.nlp.ling.HasWord;
import edu.stanford.nlp.ling.Sentence;
import edu.stanford.nlp.trees.*;
import edu.stanford.nlp.parser.lexparser.LexicalizedParser;
import org.json.simple.JSONObject;
import org.json.simple.JSONArray;
import org.json.simple.parser.ParseException;
import org.json.simple.parser.JSONParser;


class VerbPairFinder {

  /**
   * The main method demonstrates the easiest way to load a parser.
   */
  public static void main(String[] args) {


    if (args.length == 2) {
      String parserModel = "edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz";

      LexicalizedParser lp = LexicalizedParser.loadModel(parserModel);
      List <String> content = read_file(args[0]);
      JSONObject entity_content = read_entity_file(args[1]);
      JSONObject result= new JSONObject();
      for (int i=0;i<content.size();i++){
        Integer temp_int = i+1;
        String index = temp_int.toString();
        JSONObject sub_data = (JSONObject) entity_content.get(index);
        String entity = (String)sub_data.get("entity");
        List <String> sentence_verbs = find_verb_pair_in_sentence(lp,entity,content.get(i));
        JSONArray verb_array = new JSONArray();
        for(int j=0;j<sentence_verbs.size();j++){
          verb_array.add(sentence_verbs.get(i));
        }
        sub_data.put("verbs",verb_array);
        result.put(index,sub_data);
      }
    } else {
      System.out.println("ERROR: use file_name and entity file as input!");
    }
  }

  public static List <String> read_file(String file_name){
    try (BufferedReader br = new BufferedReader(new FileReader(file_name))) {
      String line;
      List <String> content = new ArrayList<String>();
      while ((line = br.readLine()) != null) {
       // process the line.
        content.add(line);

      }
      return content;
    }
    catch(FileNotFoundException fe){
        System.out.println("Cannot find file "+file_name);
        System.out.println(fe);

    } 

  }


  public static JSONObject read_entity_file(String file_path){
    JSONParser parser = new JSONParser();
    String content = new Scanner(new File(file_path)).useDelimiter("\\Z").next();
    JSONObject obj = parser.parse(content);
    JSONObject loaded_obj = (JSONObject) obj;
    return loaded_obj;
        //System.out.println("Loaded size: "+ loaded_obj.size());
        
  }


  /**
   * find_verb_pair_in_sentence takes a sentence and an entity as input,
   * and return the verb-entity back 
   */
  public static List <String> find_verb_pair_in_sentence(LexicalizedParser lp, String entity, String sentence) {
    // This option shows parsing a list of correctly tokenized words
    


    // This option shows loading and using an explicit tokenizer
    TokenizerFactory<CoreLabel> tokenizerFactory =
        PTBTokenizer.factory(new CoreLabelTokenFactory(), "");
    Tokenizer<CoreLabel> tok =
        tokenizerFactory.getTokenizer(new StringReader(sentence));
    List<CoreLabel> rawWords2 = tok.tokenize();
    Tree parse = lp.apply(rawWords2);

    TreebankLanguagePack tlp = lp.treebankLanguagePack(); // PennTreebankLanguagePack for English
    GrammaticalStructureFactory gsf = tlp.grammaticalStructureFactory();
    GrammaticalStructure gs = gsf.newGrammaticalStructure(parse);
    List<TypedDependency> tdl = gs.typedDependenciesCCprocessed();

    List <String> verbs = new ArrayList<String>();
    for (int i=0;i<tdl.size();i++){
        System.out.println(tdl.get(i).reln().getShortName());
  
        String rel = tdl.get(i).reln().getShortName().toString();
        if (rel.equals("root")){
		      continue;
        }
        String d_tag = tdl.get(i).dep().tag();
        String g_tag = tdl.get(i).gov().tag();
        String d_word = tdl.get(i).dep().word();
        String g_word = tdl.get(i).gov().word();
        if(g_word.equals(entity) ){
            if (d_tag.contains("VB") ){
                //System.out.println("Found!");
                //System.out.println(d_word+" "+g_word+" "+rel);
                verbs.add(d_word);
            } 
        }
        else if(d_word.equals(entity) ){
            if (g_tag.contains("VB") ){
                //System.out.println("Found!");
                //System.out.println(d_word+" "+g_word+" "+rel);
                verbs.add(g_word);
            }
        }

        //System.out.println(word+" / "+tag);
        //System.out.println(tdl.get(i).gov());
    }
    return verbs;
    // You can also use a TreePrint object to print trees and dependencies
    //TreePrint tp = new TreePrint("penn,typedDependenciesCollapsed");
    //tp.printTree(parse);
  }

  private VerbPairFinder() {} // static methods only

}
