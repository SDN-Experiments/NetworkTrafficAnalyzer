package extraiatributos;


import static extraiatributos.ExtraiAtributos.CLASSE;
import java.io.IOException;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;
import jpcap.JpcapCaptor;
import jpcap.NetworkInterface;

public class ExtraiAtributos {

    static NetworkInterface[] array;
    static JpcapCaptor fluxoAlvo;
    static JpcapCaptor fluxoCompletos_pCap;
    static ArrayList<String> saida = new ArrayList<String>();
    static final String CLASSE = "web";
    static String url_fluxos_rotulados = "C:\\Users\\Matheus\\eclipse-workspace\\ExtrairAtributos\\Fluxos Rotulados\\web\\" + CLASSE;
	static Path file = Paths.get("weka_input_" + CLASSE + ".arff");

    public static void escreveCabecalho () throws IOException {
		//Escreve o cabeçalho do arquivo de input do Weka
		List<String> cabecalho = new ArrayList();

		cabecalho.add("@ATTRIBUTE TamanhoJanela			NUMERIC");
		cabecalho.add("@ATTRIBUTE TamanhoPayload			NUMERIC");
		cabecalho.add("@ATTRIBUTE CompCabecalhoTCP		NUMERIC");
		cabecalho.add("@ATTRIBUTE CompPacote		                NUMERIC");
		cabecalho.add("@ATTRIBUTE class 					{p2p,web, ftp}");
		cabecalho.add("");
		cabecalho.add("");
		cabecalho.add("");
		
		//Ficar atento com problemas de codificação caso o Weka dê erro.
		Files.write(file, cabecalho, Charset.forName("UTF-8"));
    }
    
    public static void main(String[] args) throws IOException {
    	
    	escreveCabecalho();
    	
    	for (int i = 1; i < 2; i++) {
            try {
            	System.out.println(url_fluxos_rotulados);
                fluxoAlvo = JpcapCaptor.openFile(url_fluxos_rotulados + "\\Fluxo (" + i + ").pcap");
                extraiatributos.extrairtcp.extraindo(fluxoAlvo);
            } catch (IOException ex) {
                Logger.getLogger(extrairtcp.class.getName()).log(Level.SEVERE, null, ex);
            } finally {
                fluxoAlvo.close();
            }

        }
    }
}
