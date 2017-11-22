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

public class Extrair_tcp_udp {

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

        SummaryStatistics tamtotal_pacote = new SummaryStatistics();
        SummaryStatistics comp_cabecalhoip = new SummaryStatistics();
        SummaryStatistics comp_cabecalho_protocolo = new SummaryStatistics();
        
        Frequency codigo_protocolo = new Frequency();

        Frequency numero_srcport = new Frequency();
        Frequency numero_dstport = new Frequency();

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

        //percorrendo a lista de pacotes para calcular os atributos
        for (Packet packet : pacotes) {
            //IPPacket, aqui ficam os atributos que sao comum ao TCP e UDP
            if (packet instanceof IPPacket) {
                IPPacket pacote = (IPPacket) packet;

                tamtotal_pacote.addValue(pacote.len); // tamanho total ou comprimento do pacote, cabeçalho + dados, pode ter tamanho mínimo é de vinte bytes e o máximo é 64 Kb                                

                codigo_protocolo.addValue(((IPPacket) pacote).protocol); // Indica o protocolo (presente no campo de dados) que pediu o envio do datagrama, através de um código numérico, exemplos: - 01 ICMP  - 06 TCP - 17 UDP
                
                comp_cabecalhoip.addValue(pacote.header.length); //comprimento do cabecalho (sem dados), na teoria, pode ter no maximo 60 bytes
                
                comp_cabecalho_protocolo.addValue(pacote.length-20);
            }
            if (packet instanceof TCPPacket) {
                TCPPacket pacote_tcp = (TCPPacket) packet;
                
               // tam_cabecalho.addValue(((TCPPacket)pacote_tcp).header.length); 
                numero_srcport.addValue(((TCPPacket) pacote_tcp).src_port);
                numero_dstport.addValue(((TCPPacket) pacote_tcp).dst_port);
            }                                                              //Get Porta de Origem e destino  
            if (packet instanceof UDPPacket) {
                UDPPacket pacote_udp = (UDPPacket) packet;
                
               // tam_cabecalho.addValue(((UDPPacket)pacote_udp).header.length); //comprimento do cabecalho, na teoria, pode ter no maximo 60 bytes
                numero_srcport.addValue(((UDPPacket) pacote_udp).src_port);
                numero_dstport.addValue(((UDPPacket) pacote_udp).dst_port);
            }

        }        

        System.out.println("Dados do tamanho do pacote");
        //Pacote completo - media, desvio padrao, variancia, valor maximo;
        double tamtotal_medio_pacote = tamtotal_pacote.getMean();
        double desvio_padrao_pacote = tamtotal_pacote.getStandardDeviation();
        double variancia_pacote = tamtotal_pacote.getVariance();
        double maximo_pacote = tamtotal_pacote.getMax();
        double min_pacote = tamtotal_pacote.getMin();     
        
        BigDecimal ttmp = new BigDecimal(tamtotal_medio_pacote).setScale(5, RoundingMode.HALF_EVEN);
        BigDecimal dpp = new BigDecimal(desvio_padrao_pacote).setScale(5, RoundingMode.HALF_EVEN);
        BigDecimal vp = new BigDecimal(variancia_pacote).setScale(5, RoundingMode.HALF_EVEN);
        
        System.out.println("tamtotal_med_pacote:     " + (ttmp.doubleValue()));
        System.out.println("desv_padrao_tamtotal:    " + (dpp.doubleValue()));
        System.out.println("variancia_tamtotal:      " + (vp.doubleValue()));
        System.out.println("tamtotal. pacote_maior:  " + maximo_pacote);
        System.out.println("tamtotal. pacote_menor:  " + min_pacote);
                     
        System.out.println();
        
        System.out.println("Dados do tamanho do cabecalho");
        //Cabecalho - media, desvio padrao e variancia;
        double comp_medio_cabecalhoip = comp_cabecalhoip.getMean();
        double desvio_padrao_cabecalhoip = comp_cabecalhoip.getStandardDeviation();
        double variancia_cabecalhoip = comp_cabecalhoip.getVariance();
        
        BigDecimal cmcip = new BigDecimal(comp_medio_cabecalhoip).setScale(5, RoundingMode.HALF_EVEN);
        BigDecimal dpcip = new BigDecimal(desvio_padrao_cabecalhoip).setScale(5, RoundingMode.HALF_EVEN);
        BigDecimal vcip = new BigDecimal(variancia_cabecalhoip).setScale(5, RoundingMode.HALF_EVEN);
        
        System.out.println("Comp. med cabecalhoIP:   " + (cmcip.doubleValue()));
        System.out.println("desv_padrao_cabecalhoIP: " + (dpcip.doubleValue()));
        System.out.println("variancia_cabecalhoIP:   " + (vcip.doubleValue()));
        
        //Numero do protocolo - moda (que mais se repete entre os pacotes do .pcap)
        List<Comparable<?>> moda_protocolo = codigo_protocolo.getMode();

        //Pega a porta que mais se repete entre os pacotes do .pcap
        List<Comparable<?>> moda_srcporta = numero_srcport.getMode();
        List<Comparable<?>> moda_dstporta = numero_dstport.getMode();

        System.out.println();       
        System.out.println("Protocolo frequente: "+moda_protocolo.get(0));
        System.out.println("Porta src: "+moda_srcporta.get(0));
        System.out.println("Porta dst: "+moda_dstporta.get(0));

        System.out.println("---------------------------------------------------------");

        List<String> fluxos = new ArrayList<>();

        fluxos.add(
                ttmp + "," + dpp + "," + vp + "," + maximo_pacote + "," + min_pacote + ","
                + cmcip + "," + dpcip + "," + vcip + ","
                + moda_protocolo.get(0) + ","
                + moda_srcporta.get(0) + "," + moda_dstporta.get(0) + ","
                + CLASSE
        );
        escreveArquivo(fluxos);

    }
}
