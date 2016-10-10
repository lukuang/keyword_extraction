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
import java.nio.charset.Charset;



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
        //private List<Tree> phrase_children =new  ArrayList<Tree> ();
        //private List<Tree> clause_children = new ArrayList<Tree> ();
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
                                        //phrase_children.add(child);
                                        BasicItem sub_phrase = new BasicItem(child,false);

                                        leafs.addAll(sub_phrase.get_leafs());
                                        clauses.addAll(sub_phrase.get_clauses());
                                }
                        }
                        else{
                                //Clause sub_clause = new Clause(child);
                                //clause_children.add(child);
                                BasicItem sub_clause = new BasicItem(child,true);
                                clauses.addAll(sub_clause.get_clauses());

                        }

                }


                // for(int j=0; j<clause_children.size();j++){

                //         Tree clause_child = clause_children.get(j);

                //         BasicItem sub_clause = new BasicItem(clause_child,true);
                //         clauses.addAll(sub_clause.get_clauses());


                // }

                // for(int k=0; k<phrase_children.size(); k++){
                //         Tree phrase_child = phrase_children.get(k);

                //         BasicItem sub_phrase = new BasicItem(phrase_child,false);

                //         leafs.addAll(sub_phrase.get_leafs());
                //         clauses.addAll(sub_phrase.get_clauses());

                // }

                
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


class FindPrep {


  


  
  
  private static final class  Result_tuple{
    private String sentence;
    private String prep ;
    public Result_tuple(String sentence, String prep){
      this.sentence = sentence;
      this.prep = prep;
    }

    public Result_tuple(String prep){
      this.prep = prep;
    }

    public void set_sentence(String sentence){
      this.sentence = sentence;
    }

    public String get_sentence(){
      return sentence;
    }

    public String get_prep(){
      return prep;
    }


  }






  /**
   * The main method demonstrates the easiest way to load a parser.
   */
  public static void main(String[] args) {

    //print default character set
    System.out.println("default character set is:"+ Charset.defaultCharset());

    Integer run_num = 80;
    if (args.length == 2) {
      try{
          String parserModel = "edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz";
          String[] options = { "-maxLength", "80"};
          LexicalizedParser lp = LexicalizedParser.loadModel(parserModel,options);

          JSONArray feature_data = read_feature_file(args[0]);
          JSONArray result = new JSONArray();
          String dest_file = args[1];

          System.err.println("write to:"+dest_file);
          
          
          int i = 0;
          int processed;
          for (Object o: feature_data){
            i += 1;
            processed = i;
            if (processed%100==0){
              System.gc();
              System.gc();
              System.err.println("Processed "+processed+" sentences");
            }
            JSONObject single_data = (JSONObject) o;
            JSONObject sub_result =  single_data;
            
            String entity = (String)single_data.get("entity");
            String sentence =  (String)single_data.get("sentence");
            JSONArray original_tuples = (JSONArray)single_data.get("result_tuples");
            // if(entity.equals("National Weather Service")){
            //   System.err.println("found entity!");
            //   System.err.println("sentence index"+sentence_index_string);
            //   System.err.println("sentence text:"+sentence);
            // }else{
            //   continue;
            // }
            List< List<Tree> > clauses = find_clauses_in_sentence(lp, entity, sentence);
            

            //print_clauses(clauses);

            List<Result_tuple> result_tuples = new ArrayList<Result_tuple>();
            HashSet<String> candidates = new HashSet<String>();
            List<String> entitiy_words= get_entity_words(entity);

            //System.out.println("Sentence is:\n"+sentence);
            
            for(String single_word : entitiy_words){
                candidates.addAll(find_prep_in_sentence(lp, single_word, sentence));
            }
            
            // System.err.println("for "+entity+" candidates are:");
            // for(String candidate_verb: candidates){
            //    System.err.println(candidate_verb);
            // }
            result_tuples = find_result_tuple_in_clauses(clauses, entitiy_words,candidates);
            // System.err.println("There are "+result_tuples.size()+" tuples");
            
            for(String candidate: candidates){
              boolean has = false;
              for( Result_tuple single_tuple: result_tuples){
                if(candidate.equals(single_tuple.get_prep())){
                  has = true;
                  break;
                }
              }
              if (!has){
                System.err.println("candidate "+candidate+" does not in preps");
              }
            }

            JSONArray result_json_tuples = new JSONArray();
            if (result_tuples.isEmpty()){
              result_json_tuples = original_tuples;
            }
            else{
              for( Result_tuple single_tuple: result_tuples){
                  String now_clause = single_tuple.get_sentence();
                  String now_prep = single_tuple.get_prep();
                for (Object single_old_o: original_tuples ){
                  JSONObject single_old_tuple = (JSONObject)single_old_o;
                  String single_old_clause = (String) single_old_tuple.get("sentence"); 
                  if(single_old_clause.equals(now_clause)){
                    JSONObject single_result_tuple = new JSONObject();
                    single_result_tuple.put("sentence",now_clause);
                    single_result_tuple.put("prep", now_prep);
                    single_result_tuple.put("verb",(String)single_old_tuple.get("verb"));
                    result_json_tuples.add(single_result_tuple);
                  }
                }
              }    

            }
            
            

            sub_result.put("result_tuples",result_json_tuples);
            result.add(sub_result);

          }
          try {

              FileWriter file = new FileWriter(dest_file);
              file.write(result.toJSONString());
              file.flush();
              file.close();

          } catch (IOException e) {
              e.printStackTrace();
          }

          //System.out.println(result);
          System.out.println("finished!");
      } catch (Exception e){
          System.out.println(e);
          e.printStackTrace();
      }


    } else {
      System.err.println("ERROR: use file_name and entity file as input!");
    }
  }

  private static String get_single_clause_text(List<Tree> clause){
    String clause_text = "";
    for(Tree leaf: clause){
      List<Word> words = leaf.yieldWords();
      String word_text = "";
      word_text = words.get(0).word();
      if(words.size()!=1){
        
        for(int k =1; k<words.size();k++){
          word_text += " "+words.get(k).word();
        }

      }
      clause_text += " "+word_text;

    }
    return clause_text;
  }

  private static void print_clauses(List< List<Tree> > clauses){
      System.err.println("Clauses:");
      for(List<Tree> clause: clauses){
          //List<Tree> leafs = clause.skipRoot().getLeaves();
          String clause_text = get_single_clause_text(clause);
          System.err.println("\t"+clause_text);
      }

  }


  private static List<String> get_entity_words(String entity){
    TokenizerFactory<CoreLabel> tokenizerFactory =
        PTBTokenizer.factory(new CoreLabelTokenFactory(), "");
    Tokenizer<CoreLabel> tok =
        tokenizerFactory.getTokenizer(new StringReader(entity));
    List<CoreLabel> rawWords2 = tok.tokenize();



    List <String> entitiy_words = new ArrayList<String>();
    for (CoreLabel w: rawWords2){
      entitiy_words.add(w.word());
    }
    return entitiy_words;
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
        System.err.println("Cannot find file "+file_name);
        System.err.println(fe);

    }catch(IOException e){
      e.printStackTrace();
    }
    return content;
  }


  public static JSONArray read_feature_file(String file_path){
    JSONParser parser = new JSONParser();
    JSONArray feature_data = new JSONArray();
    try{
      String content = new Scanner(new File(file_path)).useDelimiter("\\Z").next();
    
      Object obj = parser.parse(content);
      feature_data = (JSONArray) obj;
      
        //System.out.println("Loaded size: "+ loaded_obj.size());
    }
    catch(ParseException pe){

         System.err.println("position: " + pe.getPosition());
         System.err.println(pe);
    }
    catch(FileNotFoundException fe){
        System.err.println("Cannot find file "+file_path);
        System.err.println(fe);

    }
    return feature_data; 
  }

  /**
  *find the clauses in the sentence that contain the entity
  */
  public static List< List<Tree> > find_clauses_in_sentence(LexicalizedParser lp, String entity, String sentence){
    List< List<Tree> > required_clauses = new ArrayList< List<Tree> >();
    TokenizerFactory<CoreLabel> tokenizerFactory =
        PTBTokenizer.factory(new CoreLabelTokenFactory(), "");

    if(sentence != null && !sentence.isEmpty()){
      Tokenizer<CoreLabel> tok =
          tokenizerFactory.getTokenizer(new StringReader(sentence));
      List<CoreLabel> rawWords2 = tok.tokenize();
      boolean success = true;
      // System.err.println("The sentence length is "+rawWords2.size());
      Tree parse;
      parse = lp.apply(rawWords2);
      
      Tree root = parse.skipRoot();
      if (root.label().value().equals("X")){
        // System.err.println("Skip X Tree");

        List< List<Tree> > clauses = new ArrayList< List<Tree> >();
        return clauses;

      }
    
      Clause clause_method = new Clause(root);
      List< List<Tree> > clauses = clause_method.get_clauses();
      return clauses;
     }
     else{
      List< List<Tree> > clauses = new ArrayList< List<Tree> >();
      return clauses;
     } 
  }


  private static List<Result_tuple> find_result_tuple_in_clauses(List< List<Tree> > clauses, List<String> entitiy_words, HashSet<String> candidates){
    List <Result_tuple> result_tuples = new ArrayList<Result_tuple> ();

    

    for(List<Tree> single_clause: clauses){
      if (in_clause(single_clause,entitiy_words)){
        //System.out.println("found valid clause:");
        //System.out.println("\t" + clause_text);

        result_tuples.addAll(get_result_tuples(single_clause, candidates));
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
              System.err.println("WARRNIGN: WORD SIZE BIGGER THAN 2!!");

              for(int k =1; k<words.size();k++){
                word_text += " "+words.get(k).word();
              }
              System.err.println("the word is: "+word_text);
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

  private static List< Result_tuple > get_result_tuples(List<Tree> single_clause, HashSet<String> candidates){
    String sentence_string = "";
    String prep = "";
    List< Result_tuple > result_tuples = new ArrayList<Result_tuple> ();
    HashMap<String,Integer> prep_map =  new HashMap<String,Integer>();
    for(int l=0;l<single_clause.size();l++){
            Tree node = single_clause.get(l);

            List<Word> words = node.yieldWords();
            String word_text = "";
            word_text = words.get(0).word();
            if(words.size()!=1){
              System.err.println("WARRNIGN: WORD SIZE BIGGER THAN 2!!");

              for(int k =1; k<words.size();k++){
                word_text += " "+words.get(k).word();
              }
            }
            // System.err.println("the word is: "+word_text);
            String word_label = node.label().value();
            if(l==0){
                sentence_string = word_text;
            }
            else{
                sentence_string += " " + word_text;
            }
            if(word_label.equals("IN") || word_label.equals("TO") ){
              prep = word_text; 
              if( candidates.contains(prep) && prep_map.get(prep)==null){
                // System.err.println("add prep: "+word_text);
                result_tuples.add(new Result_tuple(prep));
                prep_map.put(prep,1);
              }
              
            }
            
      }
      for(Result_tuple single_tuple: result_tuples){
        single_tuple.set_sentence(sentence_string);
      }
      return result_tuples;
  }


  /**
   * find_prep_in_sentence takes a sentence and an entity as input,
   * and return the verb-entity back 
   */
  public static List <String> find_prep_in_sentence(LexicalizedParser lp, String single_word, String sentence) {
    


    
    TokenizerFactory<CoreLabel> tokenizerFactory =
        PTBTokenizer.factory(new CoreLabelTokenFactory(), "");
    Tokenizer<CoreLabel> tok =
        tokenizerFactory.getTokenizer(new StringReader(sentence));
    List<CoreLabel> rawWords2 = tok.tokenize();
    try{
      Tree parse = lp.apply(rawWords2);
    
    

      TreebankLanguagePack tlp = lp.treebankLanguagePack(); // PennTreebankLanguagePack for English
      GrammaticalStructureFactory gsf = tlp.grammaticalStructureFactory();
      GrammaticalStructure gs = gsf.newGrammaticalStructure(parse);
      List<TypedDependency> tdl = gs.typedDependenciesCCprocessed();

      List <String> preps = find_prep_in_denpendencies(tdl,single_word);
      // You can also use a TreePrint object to print trees and dependencies
      //TreePrint tp = new TreePrint("penn,typedDependenciesCollapsed");
      //tp.printTree(parse);
      return preps;
    }
    catch(UnsupportedOperationException ue){
        System.out.println("Sentence is too long:\n"+sentence+"\n");
        System.err.println("return empty preps list");
        List <String> preps = new ArrayList<String>();
        return preps;
    }
  }

  public static List <String> find_prep_in_denpendencies(List<TypedDependency> tdl, String single_word){
    List <String> preps = new ArrayList<String>();
    List <String> denpendent_words = new ArrayList<String>();
    for (int i=0;i<tdl.size();i++){
        //System.out.println(tdl.get(i).reln().getShortName());
  
        String rel = tdl.get(i).reln().getShortName().toString();
        if (rel.equals("root")){
          continue;
        }
        String d_tag = tdl.get(i).dep().tag();
        String g_tag = tdl.get(i).gov().tag();
        String d_word = tdl.get(i).dep().originalText();
        String g_word = tdl.get(i).gov().originalText();
        //System.out.println("original pair:"+tdl.get(i).dep().word()+", "+tdl.get(i).gov().word());
        //System.out.println("new pair:"+g_word+", "+d_word);
        if(g_word.equals(single_word) ){
            if (d_tag.equals("IN") || d_tag.equals("TO") ){
                //System.out.println("Found!");
                //System.out.println(d_word+" "+g_word+" "+rel);
                preps.add(d_word);
            } 
            
        }
        else if(d_word.equals(single_word) ){
            if (g_tag.equals("IN") || g_tag.equals("TO") ){
                //System.out.println("Found!");
                //System.out.println(d_word+" "+g_word+" "+rel);
                preps.add(g_word);
            }

        }

        //System.out.println(word+" / "+tag);
        //System.out.println(tdl.get(i).gov());
    }
    return preps;
  }




  private FindPrep() {} // static methods only

}
