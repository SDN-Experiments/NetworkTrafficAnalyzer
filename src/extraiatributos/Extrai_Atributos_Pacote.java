package extraiatributos;

import static extraiatributos.ExtraiAtributos2.CLASSE;
import java.io.IOException;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.LinkOption;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardOpenOption;
import java.util.ArrayList;
import java.util.List;

import org.apache.commons.math3.stat.Frequency;
import org.apache.commons.math3.stat.descriptive.SummaryStatistics;

import jpcap.JpcapCaptor;
import jpcap.NetworkInterface;
import jpcap.PacketReceiver;
import jpcap.packet.IPPacket;
import jpcap.packet.Packet;
import jpcap.packet.TCPPacket;
import jpcap.packet.UDPPacket;

public class Extrai_Atributos_Pacote {

    static NetworkInterface[] array;
    static Path file = Paths.get("weka_input_" + CLASSE + ".arff");

    public static void escreveArquivo(List<String> fluxo) throws IOException {

        //Se o arquivo nao existe, cria.
        if (!Files.exists(file, LinkOption.NOFOLLOW_LINKS)) {
            Files.createFile(file);
        }
        Files.write(file, fluxo, Charset.forName("UTF-8"), StandardOpenOption.APPEND);
    }

    public static void extraindo(JpcapCaptor pcaptor) throws IOException {

        //lista para receber os pacotes
        final List<Packet> pacotes = new ArrayList<>();
        pcaptor.loopPacket(-1, new PacketReceiver() {
            @Override
            public void receivePacket(Packet packet) {
                if (packet instanceof IPPacket) {
                    pacotes.add(packet);
                }
            }
        });
        
        String atributo_pacote = "";
        List<String> fluxos = new ArrayList<>();
        //percorrendo a lista de pacotes para calcular os atributos
        for (Packet packet : pacotes) {
        	
        	atributo_pacote = "";
            //IPPacket, aqui ficam os atributos que sao comum ao TCP e UDP
            if (packet instanceof IPPacket) {
                IPPacket pacote = (IPPacket) packet;
                
                atributo_pacote = pacote.length + "," + pacote.data.length + "," + pacote.header.length + "," + ((IPPacket) pacote).protocol;                 
            }
            if (packet instanceof TCPPacket) {
                TCPPacket pacote_tcp = (TCPPacket) packet;
                
                atributo_pacote = atributo_pacote + "," + ((TCPPacket) pacote_tcp).src_port + "," + ((TCPPacket) pacote_tcp).dst_port;        
            }  
            if (packet instanceof UDPPacket) {
                UDPPacket pacote_udp = (UDPPacket) packet;
                
                atributo_pacote = atributo_pacote + "," + ((UDPPacket) pacote_udp).src_port + "," + ((UDPPacket) pacote_udp).dst_port;
            }
            
            fluxos.add(atributo_pacote + "," + CLASSE);
        }        
        escreveArquivo(fluxos);

    }
}
