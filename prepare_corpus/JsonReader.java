import edu.stanford.nlp.ie.AbstractSequenceClassifier;
import edu.stanford.nlp.ie.crf.*;
import edu.stanford.nlp.io.IOUtils;
import edu.stanford.nlp.ling.CoreLabel;
import edu.stanford.nlp.ling.CoreAnnotations;
import edu.stanford.nlp.sequences.DocumentReaderAndWriter;
import edu.stanford.nlp.util.Triple;
import org.json.simple.JSONObject;
import org.json.simple.JSONArray;
import org.json.simple.parser.ParseException;
import org.json.simple.parser.JSONParser;
import java.io.*;
import java.util.*;
import java.io.FileNotFoundException;

public class JsonReader {

  private Object obj;
  private JSONObject loaded_obj;
  private HashMap<String, String> narrative_map;
  private MyWrapper original_entitiy_map;
  private MyWrapper narrative_entitiy_map;

  public JsonReader (String file_path){

    narrative_map = new HashMap<String, String>();
    original_entitiy_map = new MyWrapper();
    narrative_entitiy_map = new MyWrapper();

    try{
        JSONParser parser = new JSONParser();
        String content = new Scanner(new File(file_path)).useDelimiter("\\Z").next();
        obj = parser.parse(content);
        loaded_obj = (JSONObject) obj;
        System.out.println("Loaded size: "+ loaded_obj.size());
        Iterator<?> eid = loaded_obj.keySet().iterator();
        while(eid.hasNext()){
            String key = (String)eid.next();
            if(key=="69591"){
                System.out.println("found 69591!");
            }
            JSONObject sub_data = (JSONObject) loaded_obj.get(key);
            narrative_map.put(key,(String)sub_data.get("narrative"));
            JSONArray original_entities = (JSONArray) sub_data.get("entities");
            for (int i=0;i<original_entities.size();i++){
                String name = (String)original_entities.get(i);
                original_entitiy_map.doublePut(key,name);
            }

        }
        this.get_entities_from_narrative();
    }
    catch(FileNotFoundException fe){
        System.out.println("Cannot find file "+file_path);
        System.out.println(fe);

    }
    catch(ParseException pe){

         System.out.println("position: " + pe.getPosition());
         System.out.println(pe);
    }

    
  }

  private void get_entities_from_narrative(){
    String serializedClassifier = "/home/1546/source/stanford-ner-2015-12-09/classifiers/english.all.3class.distsim.crf.ser.gz";

    try{
        AbstractSequenceClassifier<CoreLabel> classifier = CRFClassifier.getClassifier(serializedClassifier);
        List<Triple<String, Integer, Integer>> list;
        for (Map.Entry<String, String> narrative_entry : narrative_map.entrySet()){
            String eid = narrative_entry.getKey();
            String narrative = narrative_entry.getValue();
            list = classifier.classifyToCharacterOffsets(narrative);
            for (Triple<String, Integer, Integer> item : list) {
                String entitiy_type = item.first();
                String entity = narrative.substring(item.second(), item.third());
                if(entitiy_type.equals("LOCATION") || entitiy_type.equals("ORGANIZATION") ){
                    narrative_entitiy_map.doublePut(eid,entity);
                }
            }
        }
        System.out.println("now the sizes are "+original_entitiy_map.size()+" "+narrative_entitiy_map.size());
    }
    catch(IOException ioe){
        System.out.println(ioe);
    }
    catch(ClassNotFoundException ce){
        System.out.println(ce);

    }
  }

  public JSONObject get_result_json(){
    JSONObject obj = new JSONObject();
    Map<String, HashMap<String, Integer>> narrative_entitiy_hash = narrative_entitiy_map.get_hash();
    Map<String, HashMap<String, Integer>> original_entitiy_hash = original_entitiy_map.get_hash();
    for (Map.Entry<String, HashMap<String, Integer>> episode_Entry : narrative_entitiy_hash.entrySet()) {
        String eid = episode_Entry.getKey();
        

        //JSONObject entities = new JSONObject(episode_Entry.getValue(););
        JSONObject entities = new JSONObject();
        JSONObject original_entities = new JSONObject();
        JSONObject narrative_entities = new JSONObject();
        for (Map.Entry<String, Integer> original_entity_Entry : episode_Entry.getValue().entrySet()) {
            String entity = original_entity_Entry.getKey();
            Integer count = original_entity_Entry.getValue();
            original_entities.put(entity,count);
        }
        if (narrative_entitiy_hash.get(eid)!=null){
            HashMap<String, Integer> sub_narrative = narrative_entitiy_hash.get(eid);
            for (Map.Entry<String, Integer> narrative_entity_Entry : sub_narrative.entrySet()) {
                String entity = narrative_entity_Entry.getKey();
                Integer count = narrative_entity_Entry.getValue();
                if(episode_Entry.getValue().get(entity) == null){
                    narrative_entities.put(entity,count);
                }
            }
        }
        entities.put("original",original_entities);
        entities.put("narrative",narrative_entities);
        obj.put(eid, entities);    
    }
    System.out.println("result size: "+ obj.size());

    return obj;
  }


  private static class MyWrapper {
        private HashMap<String, HashMap<String, Integer>> hashX;

        public MyWrapper(){
            hashX = new HashMap<String, HashMap<String, Integer>>();
        }
        // ...
        public void doublePut(String one, String two) {
            Integer value = 1;
            if (hashX == null){
                System.out.println("NULL!!!");
            }
            if (hashX.get(one) == null ) {
                hashX.put(one, new HashMap<String, Integer>());
            }
            if (hashX.get(one).get(two)!= null){
                value = hashX.get(one).get(two)+1;
            } 
            hashX.get(one).put(two, value);
        }

        public int size(){
            return hashX.size();
        }

        public void show(){
            //StringWriter out = new StringWriter();
            //JSONValue.writeJSONString(hashX, out);
            //String jsonText = out.toString();
            //System.out.print(jsonText);
            //System.out.println(hashX);
            for (Map.Entry<String, HashMap<String, Integer>> tagEntry : hashX.entrySet()) {
                String tag = tagEntry.getKey();
                System.out.println(tag+":");
                for (Map.Entry<String, Integer> phraseEntry : tagEntry.getValue().entrySet()) {
                    String phrase = phraseEntry.getKey();
                    Integer count = phraseEntry.getValue();
                    System.out.println("\t"+phrase+":"+count);
                }
            }
        }

        public Map<String, HashMap<String, Integer>> get_hash(){
            return hashX;
        }
    }

  public static void main(String[] args) throws Exception {

    
    String file_path = args[0];
    JsonReader my_reader = new JsonReader(file_path);
    JSONObject result_json = my_reader.get_result_json();
    //System.out.println(result_json);
    
  }
}  