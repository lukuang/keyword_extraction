import edu.stanford.nlp.ie.AbstractSequenceClassifier;
import edu.stanford.nlp.ie.crf.*;
import edu.stanford.nlp.io.IOUtils;
import edu.stanford.nlp.ling.CoreLabel;
import edu.stanford.nlp.ling.CoreAnnotations;
import edu.stanford.nlp.sequences.DocumentReaderAndWriter;
import edu.stanford.nlp.util.Triple;
import java.io.File;
import java.util.*;

public class ShowEntitySentence {
  
  private static class MyPair
        {
                private final Integer start;
                private final Integer end;

                public MyPair( Integer astart, Integer aend)
                {
                        start   = astart;
                        end = aend;
                }

                public Integer start()   { return start; }
                public Integer end() { return end; }
        }


  public static void main(String[] args) throws Exception {

    

    String serializedClassifier = "/home/1546/source/Stanford/stanford-ner-2015-12-09/classifiers/english.all.3class.distsim.crf.ser.gz";


    AbstractSequenceClassifier<CoreLabel> classifier = CRFClassifier.getClassifier(serializedClassifier);

    /* For either a file to annotate or for the hardcoded text example, this
       demo file shows several ways to process the input, for teaching purposes.
    */
    String source_dir = args[0];
    File[] directories = new File(source_dir).listFiles(File::isDirectory);
    for(File path: directories){
        //System.out.println(path.getAbsolutePath() );
        File[] files = path.listFiles(File::isFile);
        for (File file_path: files){
            String abspath = file_path.getAbsolutePath();
            //System.out.println("\t"+ abspath);
            
            String fileContents = IOUtils.slurpFile(abspath);
            List<List<CoreLabel>> out = classifier.classify(fileContents);
            List<MyPair> sentence_pos = new ArrayList<MyPair>();

            for (List<CoreLabel> sentence : out) {
                Integer start=0;
                Integer end=0;
                Boolean first = true;
                for (CoreLabel word : sentence) {
                    if(first){
                        start = word.beginPosition();
                        first = false;
                    }
                    end = word.endPosition();
                }
                sentence_pos.add( new MyPair(start,end)  );
                  //System.out.println("end is "+word.endPosition());
            }
            



            //System.out.println("sentence size is: "+sentence_pos.size());


            List<Triple<String, Integer, Integer>> list = classifier.classifyToCharacterOffsets(fileContents);
            for (Triple<String, Integer, Integer> item : list) {
                String containing_sentence = "";
                
                String tag = item.first();
                String phrase = fileContents.substring(item.second(), item.third());
                for(MyPair sentence: sentence_pos){
                        if(sentence.start()<=item.second() && item.third()<=sentence.end()){
                                containing_sentence = fileContents.substring(sentence.start(),sentence.end());
                        }

                }
                containing_sentence = containing_sentence.replace("\n", " ").replace("\r", " ");
                phrase = phrase.replace("\n", " ").replace("\r", " ");
                System.out.println(tag+ ":" + phrase + ":" + containing_sentence);

            }
            //System.out.println("---");
            //break;
        }
        //System.out.println("---");
    }

  }
}  