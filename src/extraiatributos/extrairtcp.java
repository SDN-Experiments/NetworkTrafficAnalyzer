package extraiatributos;


import java.io.IOException;
import java.lang.*;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardOpenOption;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import jpcap.JpcapCaptor;
import jpcap.NetworkInterface;
import jpcap.PacketReceiver;
import jpcap.packet.IPPacket;
import jpcap.packet.Packet;
import jpcap.packet.TCPPacket;

public class extrairtcp {

	static NetworkInterface[] array;
	static Path file = Paths.get("weka_input_web.arff");

	public static void escreveArquivo (List<String> fluxo) throws IOException {
		Files.write(file, fluxo, Charset.forName("UTF-8"), StandardOpenOption.APPEND);
	}
	public static void extraindo(JpcapCaptor pcaptor) throws IOException {    	
		
		//Atributos estat�sticos
		long quant_bytes = 0;
		long maior_bytes = 0;
		long menor_bytes = 0;        
		int janela = 0;
		int payload = 0;  
		int comp_cabecalho = 0;
		long num_sequencia = 0;
		long num_ack = 0;
		int porta_origem = 0;
		int porta_dest = 0;
		List<String> fluxos = new ArrayList<>();
		
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
		int contador = 0;
		for (Packet packet : pacotes) {

			if (packet instanceof TCPPacket) {
				TCPPacket tcp = (TCPPacket) packet;
				System.out.println(tcp);

				//Pra que serve o n�mero de bytes???
				// n�mero de bytes
				quant_bytes = quant_bytes + tcp.caplen;

				if (contador==0){ //pega o menor valor na primeira interaÃ§Ã£o 
					menor_bytes = quant_bytes;
				}
				if (quant_bytes < menor_bytes){
					menor_bytes = quant_bytes; // retorna o menor valor de bytes
				}
				if(quant_bytes > maior_bytes){
					maior_bytes = quant_bytes; //retorna o maior valor
				} 

				//obtÃ©m o Tamanho da janela
				janela = janela + tcp.window;

				//obtÃ©m o tamanho do payload
				payload = payload + tcp.data.length;

				//obtÃ©m o comprimento do cabeÃ§alho TCP 
				comp_cabecalho = comp_cabecalho + tcp.header.length;

				//obtÃ©m o nÃºmero de seqÃ¼Ãªncia de pacotes.
				num_sequencia = num_sequencia + tcp.sequence;                                                                                               

				//obtÃ©m o nÃºmero dados recebidos 
				num_ack = num_ack + tcp.ack_num;

				//obtÃ©m a porta origem
				porta_origem = porta_origem + tcp.src_port;

				//obtÃ©m a porta destino
				porta_dest = porta_dest + tcp.dst_port;

				contador++;
			}

		}

		long media_janela = janela / contador; // media tamanho da janela

		int media_payload = payload / contador; //media payload

		int media_comprimento = comp_cabecalho / contador; //media comprimento do cabeÃ§alho TCP

		long media_num_sequencia = num_sequencia / contador; //media do nÃºmero de seqÃ¼Ãªncia de pacotes.

		long media_num_ack = num_ack / contador; //media do nÃºmero de dados recebidos 
		
		fluxos.add(maior_bytes+ "," +menor_bytes+ "," +janela+ "," +media_janela+ "," +payload+ "," +media_payload+ "," +comp_cabecalho+ "," + media_comprimento + "," +num_sequencia+ "," + media_num_sequencia+ "," +num_ack+ "," +media_num_ack+ ",p2p");
		escreveArquivo(fluxos);
		System.out.println(maior_bytes+ "," +menor_bytes+ "," +janela+ "," +media_janela+ "," +payload+ "," +media_payload+ "," +comp_cabecalho+ "," + media_comprimento + "," +num_sequencia+ "," + media_num_sequencia+ "," +num_ack+ "," +media_num_ack+ ",p2p");
	}
}