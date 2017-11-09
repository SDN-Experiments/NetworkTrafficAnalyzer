package extraiatributos;


import java.io.IOException;
import java.lang.*;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.LinkOption;
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

		//Se o arquivo não existe, cria.
		if (!Files.exists(file, LinkOption.NOFOLLOW_LINKS)) {
			Files.createFile(file);
		}
		Files.write(file, fluxo, Charset.forName("UTF-8"), StandardOpenOption.APPEND);
	}
	public static void extraindo(JpcapCaptor pcaptor) throws IOException {    	

		int janela = 0;
		int payload = 0;  
		int comp_cabecalhotcp = 0;
		int comp_pacote = 0;

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

			/*	if (packet instanceof TCPPacket) {
				TCPPacket tcp = (TCPPacket) packet;
				System.out.println(tcp);

				//Pra que serve o número de bytes???
				// número de bytes
				quant_bytes = quant_bytes + tcp.caplen;

				if (contador==0){ //pega o menor valor na primeira interaÃƒÂ§ÃƒÂ£o 
					menor_bytes = quant_bytes;
				}
				if (quant_bytes < menor_bytes){
					menor_bytes = quant_bytes; // retorna o menor valor de bytes
				}
				if(quant_bytes > maior_bytes){
					maior_bytes = quant_bytes; //retorna o maior valor
				} 

				//obtÃƒÂ©m o Tamanho da janela
				janela = janela + tcp.window;

				//obtÃƒÂ©m o tamanho do payload
				payload = payload + tcp.data.length;

				//obtÃƒÂ©m o comprimento do cabeÃƒÂ§alho TCP 
				comp_cabecalho = comp_cabecalho + tcp.header.length;

				//obtÃƒÂ©m o nÃƒÂºmero de seqÃƒÂ¼ÃƒÂªncia de pacotes.
				num_sequencia = num_sequencia + tcp.sequence;                                                                                               

				//obtÃƒÂ©m o nÃƒÂºmero dados recebidos 
				num_ack = num_ack + tcp.ack_num;

				//Não adianta somar o número das portas

				//obtÃƒÂ©m a porta origem
				//porta_origem = porta_origem + tcp.src_port;

				//obtÃƒÂ©m a porta destino
				//porta_dest = porta_dest + tcp.dst_port;

				contador++;
		}*/
			if (packet instanceof TCPPacket) {
				TCPPacket tcp = (TCPPacket) packet;

				//obtem o Tamanho da janela
				janela = janela + tcp.window;

				//obtem o tamanho do payload
				payload = payload + tcp.data.length;

				//obtem o comprimento do cabe�alho TCP 
				comp_cabecalhotcp = comp_cabecalhotcp + tcp.header.length;

				//obtem o comprimento do pacote
				comp_pacote = comp_pacote + tcp.length;


				contador++;
			}


		}

		/*long media_janela = janela / contador; // media tamanho da janela

		int media_payload = payload / contador; //media payload

		int media_comprimento = comp_cabecalho / contador; //media comprimento do cabeÃƒÂ§alho TCP

		long media_num_sequencia = num_sequencia / contador; //media do nÃƒÂºmero de seqÃƒÂ¼ÃƒÂªncia de pacotes.

		long media_num_ack = num_ack / contador; //media do nÃƒÂºmero de dados recebidos 
		 */

		fluxos.add(+janela+ "," +payload+ "," +comp_cabecalhotcp+ "," +comp_pacote+ ", p2p");
		escreveArquivo(fluxos);
	}
}