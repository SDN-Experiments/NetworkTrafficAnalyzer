package extraiatributos;

import java.util.ArrayList;

/*
 * Robust Network Traffic Classification Model
 * 
 */
public  class HostToHost {

	
	protected String id;
	protected int source_port;
	protected int destination_port;
	protected int source;//origem
	protected int destination;//destino
	//protected int number_packet;
	protected int qt_packets;//quantidade pacotes
	protected int current_size_packet;//tamanho do pacote atual
	protected ArrayList<Integer> values_size_packet= new ArrayList<Integer>();//valores pacotes para calcular variancia
	protected int sum_size_packet; //somatorio dos tamanho do pacote
	protected int  maximum_packets_bytes; //maior pacote
	protected int  minimum_packet_bytes  = Integer.MAX_VALUE; //menor pacote 
	protected float average_packet_bytes; //media pacote
	protected double  standard_deviation_packet_bytes; //desvio padrao
	protected float  minimum_interpacket_time = Float.MAX_VALUE; //minimo temp interpacket
 
	
	/*
	 * Inicializar o objeto sem variavel de tempo passad como parametro
	 * 
	 */
	public HostToHost(int source, int source_port, int destination, int destination_port, int size_packet){
	
	 this.source = source;
	 this.source_port = source_port;
	 this.destination = destination;
	 this.destination_port = destination_port;
	 this.current_size_packet = size_packet;
	 updateStateHostToHost(this);

	 this.id = this.toString();
	 
	}
	
	

	/*
	 * Inicializar o objeto com variavel de tempo passad como parametro
	 * 
	 */
	public HostToHost(int source, int source_port, int destination, int destination_port, int size_packet, int interval_time){
		
		 this.source = source;
		 this.source_port = source_port;
		 this.destination = destination;
		 this.destination_port = destination_port;
		 this.current_size_packet = size_packet;
		 updateStateHostToHost(this);

		 this.id = this.toString();
		 
		}
	

	/*
	 *
	 * para comparar na lista dos registros de fluxo caso ja tem igual so valores
	 *
	 */
	@Override
	public boolean equals(Object obj) {
		// TODO Auto-generated method stub
		if(obj instanceof HostToHost){
			HostToHost hth = (HostToHost)obj;
			if (this.getId().equals(hth.getId())){
				return true;
				}
		}
		return false;
	}
	

	/*
	 * Calcula a media
	 *
	 */
	protected void computeAverage(){
		average_packet_bytes =sum_size_packet/ qt_packets;
	}
	
	/*
	 * Calcula a DesvioPadrao
	 *
	 */
	protected void computeStandardDeviation(){
		standard_deviation_packet_bytes = Math.sqrt(average_packet_bytes);
	}
	
	/*
	 * Calcula a variancia
	 *
	 */
	protected float computeVariance(){
		float sum_variance = 0;
		for (Integer value_size_packet : values_size_packet) {
			sum_variance += Math.pow(value_size_packet - average_packet_bytes,2);
		}
		return sum_variance/qt_packets;
	}
	/*
	 * Atualizar maior em pacotes
	 *
	 */
	protected void checkGreaterBytesPacket(int bytesPacket){
		if (bytesPacket >maximum_packets_bytes) {
			maximum_packets_bytes = bytesPacket;
			
		}
	}
	
	/*
	 * Atualizar minimo em pacotes
	 *
	 */
	protected void checkSmallerBytesPacket(int bytesPacket){
		if (bytesPacket < minimum_packet_bytes ){
			minimum_packet_bytes = bytesPacket;
			
		}
	}
	
	/*
	 * Atualizar a variavel de intervalo tempo
	 *
	 */
	protected void checkSmallerIntervalTime(int intervalTime){
		if (minimum_interpacket_time < intervalTime ){
			minimum_packet_bytes = intervalTime;
			
		}
	}
	
	/*
	 * Atualizar minimo em pacotes
	 *@param Object Host to Host
	 *Registro do fluxo entre os hosts (client-server) ou (servidor-client) para ser atualizado
	 *
	 */
	protected void updateStateHostToHost(HostToHost hostToHost){
		//this.number_packet = hostToHost.number_packet ;
		 this.qt_packets++;
		 int current_size_packet = hostToHost.current_size_packet;
		 values_size_packet.add(current_size_packet);
		 this.sum_size_packet+= current_size_packet;
		 this.checkGreaterBytesPacket(current_size_packet);
		 this.checkSmallerBytesPacket(current_size_packet);
		 this.computeAverage();
		 this.computeStandardDeviation();
		 
		 
	}
	
	
	
	public int getSource_port() {
		return source_port;
	}

	public void setSource_port(int source_port) {
		this.source_port = source_port;
	}

	public int getDestination_port() {
		return destination_port;
	}

	public void setDestination_port(int destination_port) {
		this.destination_port = destination_port;
	}

	public int getSource() {
		return source;
	}

	public void setSource(int source) {
		this.source = source;
	}

	public int getDestination() {
		return destination;
	}

	public void setDestination(int destination) {
		this.destination = destination;
	}

	public int getQt_packets() {
		return qt_packets;
	}

	public void setQt_packets(int qt_packets) {
		this.qt_packets = qt_packets;
	}

	public int getCurrent_size_packet() {
		return current_size_packet;
	}

	public void setCurrent_size_packet(int current_size_packet) {
		this.current_size_packet = current_size_packet;
	}

	public String getId() {
		return id;
	}

	public int getSum_size_packet() {
		return sum_size_packet;
	}

	public float getAverage_packet_bytes() {
		return average_packet_bytes;
	}

	public double getStandard_deviation_packet_bytes() {
		return standard_deviation_packet_bytes;
	}

	public float getMinimum_interpacket_time() {
		return minimum_interpacket_time;
	}

	public int getMaximum_packets_bytes() {
		return maximum_packets_bytes;
	}
	protected void setMaximum_packets_bytes(int maximum_packets_bytes) {
		this.maximum_packets_bytes = maximum_packets_bytes;
	}
	public int getMinimum_packet_bytes() {
		return minimum_packet_bytes;
	}
	protected void setMinimum_packet_bytes(int minimum_packet_bytes) {
		this.minimum_packet_bytes = minimum_packet_bytes;
	}
	
	@Override
	public String toString() {
		// TODO Auto-generated method stub
		StringBuilder sb = new StringBuilder();
		sb.append(this.source);
		sb.append(this.source_port);
		sb.append(this.destination);
		sb.append(this.destination_port);
		return sb.toString();
	}
	
}
