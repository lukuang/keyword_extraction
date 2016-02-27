import edu.stanford.nlp.ie.AbstractSequenceClassifier;
import edu.stanford.nlp.ie.crf.*;
import edu.stanford.nlp.io.IOUtils;
import edu.stanford.nlp.ling.CoreLabel;
import edu.stanford.nlp.ling.CoreAnnotations;
import edu.stanford.nlp.sequences.DocumentReaderAndWriter;
import edu.stanford.nlp.util.Triple;
import java.io.File;
import java.util.List;

public class RankEntity {

  public static void main(String[] args) throws Exception {

    String serializedClassifier = "/home/1546/source/stanford-ner-2015-12-09/classifiers/english.all.3class.distsim.crf.ser.gz";


    AbstractSequenceClassifier<CoreLabel> classifier = CRFClassifier.getClassifier(serializedClassifier);

    /* For either a file to annotate or for the hardcoded text example, this
       demo file shows several ways to process the input, for teaching purposes.
    */
    String source_dir = args[0];
    String dest_dir = args[1];
    File[] directories = new File(source_dir).listFiles(File::isDirectory);
    for(File path: directories){
        System.out.println(path.getAbsolutePath() );
        File[] files = path.listFiles(File::isFile);
        for (File file_path: files){
            String abspath = file_path.getAbsolutePath();
            System.out.print("\t"+ abspath);
            
            String fileContents = IOUtils.slurpFile(abspath);
            List<List<CoreLabel>> out = classifier.classify(fileContents);
            for (List<CoreLabel> sentence : out) {
                for (CoreLabel word : sentence) {
                  System.out.print(word.word() + '/' + word.get(CoreAnnotations.AnswerAnnotation.class) + ' ');
                }
                System.out.println();
            }
            System.out.println("---");

            List<Triple<String, Integer, Integer>> list = classifier.classifyToCharacterOffsets(fileContents);
            for (Triple<String, Integer, Integer> item : list) {
                System.out.println(item.first() + ": " + fileContents.substring(item.second(), item.third()));
            }
            System.out.println("---");
            break;
        }
        System.out.println("---");
    }
  }
}  