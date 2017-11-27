package wekaoutput;

import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.Scanner;

public class Wekaoutput {

    public static void main(String[] args) {

        File arquivo = new File("arvoreJ48weka_cincoclasses.txt");
        try (InputStream in = new FileInputStream(arquivo)) {
            Scanner scan = new Scanner(in);
            int index_barra_anterior = -1;
            int cont = 1;
            while (scan.hasNext()) {
                StringBuilder temp = new StringBuilder(scan.nextLine());

                int search = temp.indexOf("(");

                if (search > -1) {
                    int col_dir = temp.indexOf(")") + 1;
                    int qt_index_som = search + (col_dir - search);
                    temp.replace(search,
                             qt_index_som, "");

                }

                int search_dois_pontos = temp.indexOf(":");
                if (search_dois_pontos > -1) {
                    temp.replace(temp.indexOf(":"), temp.indexOf(":") + 1, ": return");
                }
                int start_index_p2p = temp.indexOf("p2p");

                if (start_index_p2p > -1) {
                    int end_index_p2p = start_index_p2p + 3;
                    temp.replace(start_index_p2p, end_index_p2p, "\'p2p\'");
                }
                
                int start_index_ssl = temp.indexOf("ssl");

                if (start_index_ssl > -1) {
                    int end_index_ssl = start_index_ssl + 3;
                    temp.replace(start_index_ssl, end_index_ssl, "\'ssl\'");
                }
                int start_index_www = temp.indexOf("web");

                if (start_index_www > -1) {
                    int end_index_www = start_index_www + 3;
                    temp.replace(start_index_www, end_index_www, "\'web\'");
                }

                int start_index_ftp = temp.indexOf("ftp");

                if (start_index_ftp > -1) {
                    int end_index_ftp = start_index_ftp + 3;
                    temp.replace(start_index_ftp, end_index_ftp, "\'ftp\'");
                }

                int start_index_dns = temp.indexOf("dns");

                if (start_index_dns > -1) {
                    int end_index_dns = start_index_dns + 3;
                    temp.replace(start_index_dns, end_index_dns, "\'dns\'");
                }

                boolean greater = temp.indexOf(">") > -1 ? true : false;
                boolean smaller = temp.indexOf("<") > -1 ? true : false;
                boolean smaller_equal = temp.indexOf("<=") > -1 ? true : false;
                boolean great_equal = temp.indexOf(">=") > -1 ? true : false;
                boolean not_2points = search_dois_pontos > -1 ? false : true;

                if (not_2points && (greater || smaller || smaller_equal || great_equal)) {
                    temp.append(":");
                }

                int index_barra = temp.lastIndexOf("|");

                int index_barra_atual = index_barra > -1 ? index_barra + 1 : 0;
                if (index_barra_atual == 0) {
                    index_barra = index_barra_atual;
                } else {
                    index_barra = index_barra_atual - 1;
                }
                //System.out.println(cont);
                if (index_barra_atual <= index_barra_anterior) {
                    if (index_barra_atual == 0) {
                        temp.replace(index_barra, index_barra, "elif ");
                    } else if (index_barra_atual > 0) {
                        int temp_index_barra = index_barra + 4;
                        temp.replace(temp_index_barra, temp_index_barra, "elif ");
                    }
                } else if ((index_barra_atual > index_barra_anterior)) {
                    if (index_barra_atual == 0) {
                        temp.replace(index_barra, index_barra, "if ");
                    } else if (index_barra_atual > 0) {
                        int temp_index_barra = index_barra + 4;
                        temp.replace(temp_index_barra, temp_index_barra, "if ");
                    }

                }
                index_barra_anterior = index_barra_atual;
                String remove_barra = temp.toString();
                remove_barra = remove_barra.replace("|", " ").replace("﻿", "");

                System.out.println(remove_barra);

                cont++;

            }
        } catch (IOException ex) {
            ex.printStackTrace();
        }
    }

}
