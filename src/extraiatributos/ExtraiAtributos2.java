package extraiatributos;

import java.io.IOException;
import java.util.ArrayList;
import java.util.logging.Level;
import java.util.logging.Logger;
import jpcap.JpcapCaptor;
import jpcap.NetworkInterface;

public class ExtraiAtributos2 {

    static NetworkInterface[] array;
    static JpcapCaptor fluxoAlvo;
    static JpcapCaptor fluxoCompletos_pCap;
    static ArrayList<String> saida = new ArrayList<String>();
    static final String CLASSE = "web";
    static String url_fluxos_rotulados = "C:\\Users\\Matheus\\eclipse-workspace\\ExtrairAtributos\\Fluxos Rotulados\\web\\" + CLASSE;
    
    public static void main(String[] args) throws IOException {
    	
    	for (int i = 1; i <=10; i++) {
            try {
                fluxoAlvo = JpcapCaptor.openFile(url_fluxos_rotulados + "\\Fluxo (" + i + ").pcap");
                extraiatributos.Extrair_tcp_udp.extraindo(fluxoAlvo);
            } catch (IOException ex) {
                Logger.getLogger(Extrair_tcp_udp.class.getName()).log(Level.SEVERE, null, ex);
            } finally {
                fluxoAlvo.close();
            }

        }
    }
}
