// import edu.stanford.nlp.ie.AbstractSequenceClassifier;
// import edu.stanford.nlp.ie.crf.*;
// import edu.stanford.nlp.io.IOUtils;
// import edu.stanford.nlp.ling.CoreLabel;
// import edu.stanford.nlp.ling.CoreAnnotations;
// import edu.stanford.nlp.sequences.DocumentReaderAndWriter;
// import edu.stanford.nlp.util.Triple;
import java.nio.file;
import java.util.List;

public class RankEntity {

  public static void main(String[] args) throws Exception {

    String serializedClassifier = "/home/1546/source/stanford-ner-2015-12-09/classifiers/english.all.3class.distsim.crf.ser.gz";


    //AbstractSequenceClassifier<CoreLabel> classifier = CRFClassifier.getClassifier(serializedClassifier);

    /* For either a file to annotate or for the hardcoded text example, this
       demo file shows several ways to process the input, for teaching purposes.
    */
    String source_dir = args[0];
    String dest_dir = args[1];
    File[] directories = new File(source_dir).listFiles(File::isDirectory);
    for(File path: directories){
        System.out.print(path.getAbsolutePath() );
        System.out.println();
    }
  }
}  