			h2h = None
		    key = src + dst
		    if len(self.host2host_instance) > 0:
		    	if  key in self.host2host_instance:
		        	h2h = self.host2host_instance[key]
		        	h2h.updateStateHostToHostByPacket(payload,header_length_bytes)
		     	else:
		        	h2h = host2host(temp_port_src,  temp_port_dest,payload, header_length_bytes,ipv4_temp.proto)
		        	self.host2host_instance[key] = h2h
		    else:
		    	h2h = host2host(temp_port_src,  temp_port_dest,payload, header_length_bytes,ipv4_temp.proto)
		    	self.host2host_instance[key] = h2h
