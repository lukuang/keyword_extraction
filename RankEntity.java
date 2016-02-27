import edu.stanford.nlp.ie.AbstractSequenceClassifier;
import edu.stanford.nlp.ie.crf.*;
import edu.stanford.nlp.io.IOUtils;
import edu.stanford.nlp.ling.CoreLabel;
import edu.stanford.nlp.ling.CoreAnnotations;
import edu.stanford.nlp.sequences.DocumentReaderAndWriter;
import edu.stanford.nlp.util.Triple;
import java.io.File;
import java.util.*;

public class RankEntity {
  
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
            if (hashX.containsKey(one)) {
                hashX.put(one, new HashMap<String, Integer>());
            }
            if (!hashX.get(one).containsKey(two)){
                value = hashX.get(one).get(two)+1;
            } 
            hashX.get(one).put(two, value);
        }

        public void show(){
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

    

    String serializedClassifier = "/home/1546/source/stanford-ner-2015-12-09/classifiers/english.all.3class.distsim.crf.ser.gz";


    AbstractSequenceClassifier<CoreLabel> classifier = CRFClassifier.getClassifier(serializedClassifier);

    /* For either a file to annotate or for the hardcoded text example, this
       demo file shows several ways to process the input, for teaching purposes.
    */
    String source_dir = args[0];
    String dest_dir = args[1];
    MyWrapper counts = new MyWrapper();
    File[] directories = new File(source_dir).listFiles(File::isDirectory);
    for(File path: directories){
        System.out.println(path.getAbsolutePath() );
        File[] files = path.listFiles(File::isFile);
        for (File file_path: files){
            String abspath = file_path.getAbsolutePath();
            System.out.println("\t"+ abspath);
            
            String fileContents = IOUtils.slurpFile(abspath);

            List<Triple<String, Integer, Integer>> list = classifier.classifyToCharacterOffsets(fileContents);
            for (Triple<String, Integer, Integer> item : list) {
                String tag = item.first();
                String phrase = fileContents.substring(item.second(), item.third());
                System.out.println(tag+ ": " + phrase);
                counts.doublePut(tag,phrase);
            }
            System.out.println("---");
            break;
        }
        System.out.println("---");
    }
    counts.show();
  }
}  