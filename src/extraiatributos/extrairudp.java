package extraiatributos;


import java.lang.*;
import java.util.ArrayList;
import java.util.List;
import jpcap.JpcapCaptor;
import jpcap.NetworkInterface;
import jpcap.PacketReceiver;
import jpcap.packet.IPPacket;
import jpcap.packet.Packet;
import jpcap.packet.UDPPacket;

public class extrairudp {
    static NetworkInterface[] array;

    public static void extraindo(JpcapCaptor pcaptor) {

        long quant_bytes = 0;
        long maior_bytes = 0;
        long menor_bytes = 0;        
        int payload = 0;  
        int comp_cabecalho = 0;
        int OrigemPorta = 0;
        int porta_dest = 0;
        
        //lista para receber os pacotes
        final List<Packet> pacotes = new ArrayList<>();
        pcaptor.loopPacket(-1, new PacketReceiver() {
            @Override
            public void receivePacket(Packet packet) {
                if (packet instanceof IPPacket) {
                    pacotes.add(packet);
                    //   pacotes.add(packet);
                    //
                }
            }
        });

        //percorrendo a lista de pacotes para calcular os atributos
        int contador = 0;
        for (Packet packet : pacotes) {

            if (packet instanceof UDPPacket) {
                UDPPacket udp = (UDPPacket) packet;

                // nÃºmero de bytes
                quant_bytes = quant_bytes + udp.caplen;

                if (contador==0){ //pega o menor valor na primeira interaÃ§Ã£o 
                    menor_bytes = quant_bytes;
                }
                if (quant_bytes < menor_bytes){
                  menor_bytes = quant_bytes; // retorna o menor valor de bytes
                }
                if(quant_bytes > maior_bytes){
                 maior_bytes = quant_bytes; //retorna o maior valor
                }                                 

                //obtÃ©m o tamanho do payload
                payload = payload + udp.data.length;

                //obtÃ©m o comprimento do cabeÃ§alho TCP 
                comp_cabecalho = comp_cabecalho + udp.header.length;
               
                //obtÃ©m a porta origem
                OrigemPorta = OrigemPorta + udp.src_port;
                
                //obtÃ©m a porta destino
                porta_dest = porta_dest + udp.dst_port;
                
                contador++;
            }

        }
   

        int media_payload = payload / contador; //media payload

        int media_comprimento = comp_cabecalho / contador; //media comprimento do cabeÃ§alho TCP

        System.out.println("maior:" +maior_bytes+ " menor:" +menor_bytes+ " tamanho payload:" + payload + " media payload:" + media_payload + " comprimento:" + comp_cabecalho + " media comprimento do cabeÃ§alho:" + media_comprimento + " origem:" +OrigemPorta+ " destino:" +porta_dest+ ",dns");
    }
}
