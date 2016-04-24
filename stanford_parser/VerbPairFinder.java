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
import edu.stanford.nlp.ling.Word;




class BasicItem{


        private static final HashMap<String,Integer> clause_label;
        static{
              clause_label = new HashMap<String,Integer>();
              clause_label.put("S",1);
              clause_label.put("SBAR",1);
              clause_label.put("SBARQ",1);
              clause_label.put("SINV",1);
              clause_label.put("SQ",1);

        }

        private static final HashMap<String,Integer> phrase_label;
        static{
              phrase_label = new HashMap<String,Integer>();
              phrase_label.put("ADJP",1);
              phrase_label.put("ADVP",1);
              phrase_label.put("CONJP",1);
              phrase_label.put("FRAG",1);
              phrase_label.put("INTJ",1);
              phrase_label.put("LST",1);
              phrase_label.put("NAC",1);
              phrase_label.put("NP",1);
              phrase_label.put("NX",1);
              phrase_label.put("PP",1);
              phrase_label.put("PRN",1);
              phrase_label.put("PRT",1);
              phrase_label.put("QP",1);
              phrase_label.put("RRC",1);
              phrase_label.put("UCP",1);
              phrase_label.put("VP",1);
              phrase_label.put("WHADJP",1);
              phrase_label.put("WHAVP",1);
              phrase_label.put("WHNP",1);
              phrase_label.put("WHPP",1);
              phrase_label.put("X",1);

        }
        private Tree T;
        private List<Tree> leafs = new ArrayList<Tree> ();
        private List<Tree> phrase_children =new  ArrayList<Tree> ();
        private List<Tree> clause_children = new ArrayList<Tree> ();
        private List< List<Tree> > clauses = new ArrayList< List<Tree> >();

        public BasicItem(Tree root_node,boolean is_clause){
                init(root_node);
                if(is_clause){
                  clauses.add(leafs);
                }

        }

        private void init(Tree root_node){
            T = root_node;
            process();
        }

        public List< List<Tree> > get_clauses(){
                return clauses;
        }

        public List<Tree> get_leafs(){
                return leafs;
        }

        private void process(){
                List<Tree> children = T.getChildrenAsList();
                for(int i=0; i<children.size();i++){
                        Tree child = children.get(i); //use a deep copy of the child just to be safe
                        String label = child.label().toString();
                        if(clause_label.get(label)==null){
                                if(phrase_label.get(label)==null){
                                        leafs.add(child.deepCopy());
                                }
                                else{
                                        phrase_children.add(child);
                                }
                        }
                        else{
                                //Clause sub_clause = new Clause(child);
                                clause_children.add(child);

                        }

                }


                for(int j=0; j<clause_children.size();j++){

                        Tree clause_child = clause_children.get(j);

                        BasicItem sub_clause = new BasicItem(clause_child,true);
                        clauses.addAll(sub_clause.get_clauses());


                }

                for(int k=0; k<phrase_children.size(); k++){
                        Tree phrase_child = phrase_children.get(k);

                        BasicItem sub_phrase = new BasicItem(phrase_child,false);

                        leafs.addAll(sub_phrase.get_leafs());
                        clauses.addAll(sub_phrase.get_clauses());

                }

                
        }
  }

   class Clause extends BasicItem{
    
    public Clause(Tree root_node){
      super(root_node,true);
    }

  }


  class Phrase extends BasicItem{
    public Phrase(Tree root_node){
      super(root_node,false);
    }
  }  


class VerbPairFinder {


  


  
  
  private static final class  Result_tuple{
    private String sentence;
    private String verb;
    private String verb_label;
    public Result_tuple(String sentence, String verb, String verb_label){
      this.sentence = sentence;
      this.verb = verb;
      this.verb_label = verb_label;
    }

    public String get_sentence(){
      return sentence;
    }

    public String get_verb(){
      return verb;
    }

    public String get_verb_label(){
      return verb_label;
    }
  }






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
        JSONObject sub_result = new JSONObject();
        Integer sentence_index = i+1;
        String sentence_index_string = sentence_index.toString();
        JSONObject sub_data = (JSONObject) entity_content.get(sentence_index_string);
        String entity = (String)sub_data.get("entity");
        String sentence =  content.get(i);
        List< List<Tree> > clauses = find_clauses_in_sentence(lp, entity, sentence);
        List<Result_tuple> result_tuples = find_result_tuple_in_clauses(clauses, entity);

        sub_result.put("instance", sub_data.get("instance"));
        sub_result.put("entity", sub_data.get("entity"));
        JSONArray result_json_tuples = new JSONArray();
        for( Result_tuple single_tuple: result_tuples){
          JSONObject single_result_tuple = new JSONObject();
          single_result_tuple.put("sentence", single_tuple.get_sentence());
          single_result_tuple.put("verb", single_tuple.get_verb());
          single_result_tuple.put("verb_label", single_tuple.get_verb_label());
          result_json_tuples.add(single_result_tuple);
        }
        sub_result.put("result_tuples",result_json_tuples);
        result.put(sentence_index_string,sub_result);

        //TODO make return tuple into json and write it out
      }

      System.out.println(result);


    } else {
      System.out.println("ERROR: use file_name and entity file as input!");
    }
  }

  public static List <String> read_file(String file_name){
    List <String> content = new ArrayList<String>();
    try (BufferedReader br = new BufferedReader(new FileReader(file_name))) {
      String line;
      
      while ((line = br.readLine()) != null) {
       // process the line.
        content.add(line);

      }
      
    }
    catch(FileNotFoundException fe){
        System.out.println("Cannot find file "+file_name);
        System.out.println(fe);

    }catch(IOException e){
      e.printStackTrace();
    }
    return content;
  }


  public static JSONObject read_entity_file(String file_path){
    JSONParser parser = new JSONParser();
    JSONObject loaded_obj = new JSONObject();
    try{
      String content = new Scanner(new File(file_path)).useDelimiter("\\Z").next();
    
      Object obj = parser.parse(content);
      loaded_obj = (JSONObject) obj;
      
        //System.out.println("Loaded size: "+ loaded_obj.size());
    }
    catch(ParseException pe){

         System.out.println("position: " + pe.getPosition());
         System.out.println(pe);
    }
    catch(FileNotFoundException fe){
        System.out.println("Cannot find file "+file_path);
        System.out.println(fe);

    }
    return loaded_obj; 
  }

  /**
  *find the clauses in the sentence that contain the entity
  */
  public static List< List<Tree> > find_clauses_in_sentence(LexicalizedParser lp, String entity, String sentence){
    List< List<Tree> > required_clauses = new ArrayList< List<Tree> >();
    TokenizerFactory<CoreLabel> tokenizerFactory =
        PTBTokenizer.factory(new CoreLabelTokenFactory(), "");
    Tokenizer<CoreLabel> tok =
        tokenizerFactory.getTokenizer(new StringReader(sentence));
    List<CoreLabel> rawWords2 = tok.tokenize();
    Tree parse = lp.apply(rawWords2);
    Tree root = parse.skipRoot();
    Clause clause_method = new Clause(root);
    List< List<Tree> > clauses = clause_method.get_clauses();
    return clauses;
  }


  private static List<Result_tuple> find_result_tuple_in_clauses(List< List<Tree> > clauses, String entity){
    List <Result_tuple> result_tuples = new ArrayList<Result_tuple> ();

    TokenizerFactory<CoreLabel> tokenizerFactory =
        PTBTokenizer.factory(new CoreLabelTokenFactory(), "");
    Tokenizer<CoreLabel> tok =
        tokenizerFactory.getTokenizer(new StringReader(entity));
    List<CoreLabel> rawWords2 = tok.tokenize();



    List <String> entitiy_words = new ArrayList<String>();
    for (CoreLabel w: rawWords2){
      entitiy_words.add(w.word());
    }

    for(List<Tree> single_clause: clauses){
      if (in_clause(single_clause,entitiy_words)){
        result_tuples.addAll(get_result_tuples(single_clause));
      }
    }
    return result_tuples;
  }



  private static boolean in_clause(List<Tree> single_clause, List<String> entitiy_words){
      List<String> clause_words = new ArrayList<String>();

      for(int l=0;l<single_clause.size();l++){
            Tree node = single_clause.get(l);
            List<Word> words = node.yieldWords();
            String word_text = "";
            word_text = words.get(0).word();
            if(words.size()!=1){
              System.out.println("WARRNIGN: WORD SIZE BIGGER THAN 2!!");

              for(int k =1; k<words.size();k++){
                word_text += " "+words.get(k).word();
              }
              System.out.println("the word is: "+word_text);
            }
            clause_words.add(word_text);
            
      }

      for(String word: entitiy_words){
        if(!clause_words.contains(word)){
          return false;
        }
      }
      return true;

  }

  private static List< Result_tuple > get_result_tuples(List<Tree> single_clause){
    String sentence_string = "";
    String verb = "";
    String verb_label = "";
    List< Result_tuple > result_tuples = new ArrayList<Result_tuple> ();
    for(int l=0;l<single_clause.size();l++){
            Tree node = single_clause.get(l);

            List<Word> words = node.yieldWords();
            String word_text = "";
            word_text = words.get(0).word();
            if(words.size()!=1){
              System.out.println("WARRNIGN: WORD SIZE BIGGER THAN 2!!");

              for(int k =1; k<words.size();k++){
                word_text += " "+words.get(k).word();
              }
              System.out.println("the word is: "+word_text);
            }
            String word_label = node.label().value();
            if(word_label.contains("VB")){
              verb = word_text; 
              verb_label = word_label;
              if(l==0){
                sentence_string = word_text;
              }
              else{
                sentence_string += " " + word_text;
              }
              result_tuples.add( new Result_tuple(sentence_string,verb, verb_label) );

            }
            
      }
      return result_tuples;
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

    List <String> verbs = find_verb_pair_in_denpendencies(tdl,entity);
    // You can also use a TreePrint object to print trees and dependencies
    //TreePrint tp = new TreePrint("penn,typedDependenciesCollapsed");
    //tp.printTree(parse);
    return verbs;
  }

  public static List <String> find_verb_pair_in_denpendencies(List<TypedDependency> tdl, String entity){
    List <String> verbs = new ArrayList<String>();
    List <String> denpendent_words = new ArrayList<String>();
    for (int i=0;i<tdl.size();i++){
        //System.out.println(tdl.get(i).reln().getShortName());
  
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
            else{
                denpendent_words.add(d_word);
            }
        }
        else if(d_word.equals(entity) ){
            if (g_tag.contains("VB") ){
                //System.out.println("Found!");
                //System.out.println(d_word+" "+g_word+" "+rel);
                verbs.add(g_word);
            }
            else{
                denpendent_words.add(g_word);

            }
        }

        //System.out.println(word+" / "+tag);
        //System.out.println(tdl.get(i).gov());
    }
    if (verbs.size()!=0){
      return verbs;
    }
    else{
      List<String> old_words = new ArrayList<String>();
      old_words.add(entity);
      return remove_duplicate(find_verb_pair_in_denpendencies(tdl,denpendent_words,old_words) );
    }
  }


  public static List <String> find_verb_pair_in_denpendencies(List<TypedDependency> tdl, List <String> denpendent_words,
                    List <String> old_words){
    List <String> verbs = new ArrayList<String>();
    List <String> new_denpendent_words = new ArrayList<String>();
    for(int j =0; j<denpendent_words.size(); j++){
      String entity = denpendent_words.get(j);
      for (int i=0;i<tdl.size();i++){
        //System.out.println(tdl.get(i).reln().getShortName());
  
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
            else{
              if(!old_words.contains(d_word)){
                new_denpendent_words.add(d_word);
              }

            }
        }
        else if(d_word.equals(entity) ){
            if (g_tag.contains("VB") ){
                //System.out.println("Found!");
                //System.out.println(d_word+" "+g_word+" "+rel);
                verbs.add(g_word);
            }
            else{
              if(!old_words.contains(g_word)){
                new_denpendent_words.add(g_word);
              }

            }
        }

        //System.out.println(word+" / "+tag);
        //System.out.println(tdl.get(i).gov());
      }
      old_words.add(entity);
    }
    if(verbs.size()!=0){
      return remove_duplicate(verbs);
    }
    else{
      return remove_duplicate(find_verb_pair_in_denpendencies(tdl,new_denpendent_words,old_words) );
      
    }

  }


  public static List<String> remove_duplicate(List<String> al){
    Set<String> hs = new HashSet<>();
    hs.addAll(al);
    al.clear();
    al.addAll(hs);
    return al;
  }

  private VerbPairFinder() {} // static methods only

}
