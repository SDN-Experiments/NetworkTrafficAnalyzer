#!/usr/bin/python
# -*- coding: utf-8 -*-
	def weka_decision_tree(tamtotal_med_pacote, desv_padrao_tamtotal, variancia_tamtotal, tamtotal_pacote_maior, tamtotal_pacote_menor, com_med_cabecalhoIP, codigo_protocolo, srcporta, dstporta):
	if codigo_protocolo <= 6:
    if tamtotal_pacote_menor <= 54: return "ftp" 
    elif tamtotal_pacote_menor > 54:
        if dstporta <= 80: return "web" 
        elif dstporta > 80:
            if srcporta <= 2632: return "web" 
            elif srcporta > 2632:
                if tamtotal_pacote_menor <= 60:
                    if dstporta <= 7957:
                        if dstporta <= 443: return "web" 
                        elif dstporta > 443: return "p2p" 
                    elif dstporta > 7957: return "p2p" 
                elif tamtotal_pacote_menor > 60:
                    if tamtotal_pacote_maior <= 81: return "ftp" 
                    elif tamtotal_pacote_maior > 81: return "p2p" 
elif codigo_protocolo > 6: return "dns" 
