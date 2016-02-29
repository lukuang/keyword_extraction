import edu.stanford.nlp.ie.AbstractSequenceClassifier;
import edu.stanford.nlp.ie.crf.*;
import edu.stanford.nlp.io.IOUtils;
import edu.stanford.nlp.ling.CoreLabel;
import edu.stanford.nlp.ling.CoreAnnotations;
import edu.stanford.nlp.sequences.DocumentReaderAndWriter;
import edu.stanford.nlp.util.Triple;
import java.io.File;
import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.lang.Math;

public class RankEntityDFDiscounted {
  
  private static class MyWrapper {
        private HashMap<String, HashMap<String, Double>> hashX;

        public MyWrapper(){
            hashX = new HashMap<String, HashMap<String, Double>>();
        }
        // ...
        public void doublePut(String one, String two, Double value) {
            if (hashX == null){
                System.out.println("NULL!!!");
            }
            if (hashX.get(one) == null ) {
                hashX.put(one, new HashMap<String, Double>());
            }
            if (hashX.get(one).get(two)!= null){
                value += hashX.get(one).get(two);
            } 
            hashX.get(one).put(two, value);
        }

        public void show(){
            //StringWriter out = new StringWriter();
            //JSONValue.writeJSONString(hashX, out);
            //String jsonText = out.toString();
            //System.out.print(jsonText);
            //System.out.println(hashX);
            for (Map.Entry<String, HashMap<String, Double>> tagEntry : hashX.entrySet()) {
                String tag = tagEntry.getKey();
                System.out.println(tag+":");
                for (Map.Entry<String, Double> phraseEntry : tagEntry.getValue().entrySet()) {
                    String phrase = phraseEntry.getKey();
                    Double count = phraseEntry.getValue();
                    System.out.println("\t"+phrase+":"+count);
                }
            }
        }

        public Map<String, HashMap<String, Double>> get_hash(){
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
    //String dest_dir = args[1];
    MyWrapper counts = new MyWrapper();
    File[] directories = new File(source_dir).listFiles(File::isDirectory);
    for(File path: directories){
        //System.out.println(path.getAbsolutePath() );
        File[] files = path.listFiles(File::isFile);
        for (File file_path: files){
            String abspath = file_path.getAbsolutePath();
            //System.out.println("\t"+ abspath);
            HashMap <String, Integer> file_hash = new HashMap <String, Integer>();
            String name = file_path.getName();
            String pattern = "(\\d+)-\\d+";
            Pattern r = Pattern.compile(pattern);
            Matcher m = r.matcher(name);
            Double value = 0;
            if (m.find( )) {
                value = 1/(Math.log(Double.parseDouble(m.group(1)))/Math.log(2.0));
            }
            else{
                continue;
            }

            String fileContents = IOUtils.slurpFile(abspath);

            List<Triple<String, Integer, Integer>> list = classifier.classifyToCharacterOffsets(fileContents);
            for (Triple<String, Integer, Integer> item : list) {
                String tag = item.first();
                String phrase = fileContents.substring(item.second(), item.third());
                String combine =  tag+phrase;
                if ( file_hash.get(combine)==null ){
                    file_hash.put(combine,1);
                    counts.doublePut(tag,phrase, value);
                }
                //System.out.println(tag+ ": " + phrase);
                //counts.doublePut(tag,phrase);
            }
            
            //System.out.println("---");
            //break;
        }
        //System.out.println("---");
    }
    counts.show();
  }
}  