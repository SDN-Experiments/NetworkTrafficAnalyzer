﻿#!/usr/bin/python
# -*- coding: utf-8 -*-
def weka_decision_tree(TamahoPayload, TamanhoJanela, CompPacoteIp, comp_cabecalhotcp ):
    if TamanhoPayload <= 136:
        if CompPacoteIp <= 430:
            if TamanhoPayload <= 67:
                return 'ftp'
            elif TamanhoPayload > 67:
                return 'p2p'
        elif CompPacoteIp > 430:
            return 'p2p'
    elif TamanhoPayload > 136:
        if TamanhoJanela <= 170584:
            if TamanhoJanela <= 39479:
                if TamanhoPayload <= 3467:
                    if TamanhoJanela <= 23770:
                        if TamanhoJanela <= 15210:
                            return 'web'
                        elif TamanhoJanela > 15210:
                            return 'p2p'
                    elif TamanhoJanela > 23770:
                        if comp_cabecalhotcp <= 1136:
                            if comp_cabecalhotcp <= 688:
                                return 'web'
                            elif comp_cabecalhotcp > 688:
                                if TamanhoJanela <= 26193:
                                    return 'web'
                                elif TamanhoJanela > 26193:
                                    if TamanhoJanela <= 36266:
                                        if TamanhoJanela <= 28778:
                                            if CompPacoteIp <= 2160:
                                                return 'p2p'
                                            elif CompPacoteIp > 2160:
                                                return 'web'
                                        elif TamanhoJanela > 28778:
                                            return 'p2p'
                                    elif TamanhoJanela > 36266:
                                        return 'web'
                        elif comp_cabecalhotcp > 1136:
                            if comp_cabecalhotcp <= 2310:
                                return 'p2p'
                            elif comp_cabecalhotcp > 2310:
                                if CompPacoteIp <= 4415:
                                    return 'ftp'
                                elif CompPacoteIp > 4415:
                                    return 'p2p'
                elif TamanhoPayload > 3467:
                    if comp_cabecalhotcp <= 2608:
                        return 'web'
                    elif comp_cabecalhotcp > 2608:
                        if TamanhoPayload <= 35386:
                            return 'p2p'
                        elif TamanhoPayload > 35386:
                            if TamanhoJanela <= 36418:
                                return 'web'
                            elif TamanhoJanela > 36418:
                                if comp_cabecalhotcp <= 5004:
                                    return 'p2p'
                                elif comp_cabecalhotcp > 5004:
                                    if CompPacoteIp <= 171812:
                                        return 'web'
                                    elif CompPacoteIp > 171812:
                                        return 'p2p'
            elif TamanhoJanela > 39479:
                if TamanhoPayload <= 82566:
                    if TamanhoJanela <= 47517:
                        if comp_cabecalhotcp <= 1294:
                            return 'web'
                        elif comp_cabecalhotcp > 1294:
                            if CompPacoteIp <= 3271:
                                return 'ftp'
                            elif CompPacoteIp > 3271:
                                if CompPacoteIp <= 17321:
                                    return 'p2p'
                                elif CompPacoteIp > 17321:
                                    if CompPacoteIp <= 39769:
                                        return 'web'
                                    elif CompPacoteIp > 39769:
                                        return 'p2p'
                    elif TamanhoJanela > 47517:
                        if comp_cabecalhotcp <= 4668:
                            return 'web'
                        elif comp_cabecalhotcp > 4668:
                            if CompPacoteIp <= 46843:
                                return 'p2p'
                            elif CompPacoteIp > 46843:
                                return 'web'
                elif TamanhoPayload > 82566:
                    if TamanhoJanela <= 108317:
                        if CompPacoteIp <= 355937:
                            return 'p2p'
                        elif CompPacoteIp > 355937:
                            return 'web'
                    elif TamanhoJanela > 108317:
                        if CompPacoteIp <= 278656:
                            return 'web'
                        elif CompPacoteIp > 278656:
                            return 'p2p'
        elif TamanhoJanela > 170584:
            if TamanhoJanela <= 12945544:
                if CompPacoteIp <= 600:
                    return 'web'
                elif CompPacoteIp > 600:
                    if comp_cabecalhotcp <= 568:
                        if TamanhoJanela <= 273558:
                            return 'ftp'
                        elif TamanhoJanela > 273558:
                            if TamanhoJanela <= 328217:
                                return 'web'
                            elif TamanhoJanela > 328217:
                                if comp_cabecalhotcp <= 474:
                                    return 'ftp'
                                elif comp_cabecalhotcp > 474:
                                    if CompPacoteIp <= 1857:
                                        return 'p2p'
                                    elif CompPacoteIp > 1857:
                                        return 'ftp'
                    elif comp_cabecalhotcp > 568:
                        if TamanhoPayload <= 4922:
                            if TamanhoJanela <= 630655:
                                if TamanhoPayload <= 225:
                                    return 'p2p'
                                elif TamanhoPayload > 225:
                                    if comp_cabecalhotcp <= 1014:
                                        if TamanhoPayload <= 1115:
                                            if TamanhoJanela <= 486442:
                                                if TamanhoJanela \
    <= 409674:
                                                    return 'web'
                                                elif TamanhoJanela \
    > 409674:
                                                    if comp_cabecalhotcp \
    <= 738:
                                                        return 'p2p'
                                                    elif comp_cabecalhotcp \
    > 738:
                                                        return 'web'
                                            elif TamanhoJanela > 486442:
                                                return 'p2p'
                                        elif TamanhoPayload > 1115:
                                            return 'web'
                                    elif comp_cabecalhotcp > 1014:
                                        if TamanhoPayload <= 3117:
                                            if TamanhoJanela <= 206079:
                                                return 'p2p'
                                            elif TamanhoJanela > 206079:
                                                if comp_cabecalhotcp \
    <= 1398:
                                                    return 'web'
                                                elif comp_cabecalhotcp \
    > 1398:
                                                    if TamanhoJanela \
    <= 236704:
                                                        return 'web'
                                                    elif TamanhoJanela \
    > 236704:
                                                        return 'p2p'
                                        elif TamanhoPayload > 3117:
                                            return 'web'
                            elif TamanhoJanela > 630655:
                                if TamanhoJanela <= 2691633:
                                    return 'p2p'
                                elif TamanhoJanela > 2691633:
                                    return 'ftp'
                        elif TamanhoPayload > 4922:
                            if comp_cabecalhotcp <= 1770:
                                if TamanhoJanela <= 236704:
                                    return 'web'
                                elif TamanhoJanela > 236704:
                                    if TamanhoJanela <= 375881:
                                        if comp_cabecalhotcp <= 1398:
                                            return 'ftp'
                                        elif comp_cabecalhotcp > 1398:
                                            return 'web'
                                    elif TamanhoJanela > 375881:
                                        if TamanhoPayload <= 10712:
                                            if comp_cabecalhotcp <= 846:
                                                if TamanhoJanela \
    <= 517729:
                                                    return 'web'
                                                elif TamanhoJanela \
    > 517729:
                                                    return 'ftp'
                                            elif comp_cabecalhotcp \
    > 846:
                                                return 'web'
                                        elif TamanhoPayload > 10712:
                                            if TamanhoJanela <= 639512:
                                                return 'ftp'
                                            elif TamanhoJanela > 639512:
                                                if comp_cabecalhotcp \
    <= 1444:
                                                    return 'ftp'
                                                elif comp_cabecalhotcp \
    > 1444:
                                                    return 'web'
                            elif comp_cabecalhotcp > 1770:
                                if TamanhoJanela <= 560387:
                                    if TamanhoPayload <= 621997:
                                        return 'web'
                                    elif TamanhoPayload > 621997:
                                        return 'p2p'
                                elif TamanhoJanela > 560387:
                                    if comp_cabecalhotcp <= 16008:
                                        if TamanhoPayload <= 151772:
                                            if TamanhoJanela <= 3509958:
                                                if TamanhoPayload \
    <= 21990:
                                                    if TamanhoJanela \
    <= 2037460:
                                                        return 'web'
                                                    elif TamanhoJanela \
    > 2037460:
                                                        return 'p2p'
                                                elif TamanhoPayload \
    > 21990:
                                                    if comp_cabecalhotcp \
    <= 3592:
                                                        if TamanhoJanela \
    <= 1250272:
                                                            if TamanhoPayload \
    <= 32275:
                                                                if TamanhoJanela \
    <= 827803:
                                                                    return 'ftp'
                                                                elif TamanhoJanela \
    > 827803:
                                                                    return 'web'
                                                            elif TamanhoPayload \
    > 32275:
                                                                return 'ftp'
                                                        elif TamanhoJanela \
    > 1250272:
                                                            if TamanhoJanela \
    <= 2648452:
                                                                return 'web'
                                                            elif TamanhoJanela \
    > 2648452:
                                                                return 'p2p'
                                                    elif comp_cabecalhotcp \
    > 3592:
                                                        if TamanhoJanela \
    <= 1457064:
                                                            if comp_cabecalhotcp \
    <= 3884:
                                                                return 'web'
                                                            elif comp_cabecalhotcp \
    > 3884:
                                                                if TamanhoPayload \
    <= 40301:
                                                                    return 'p2p'
                                                                elif TamanhoPayload \
    > 40301:
                                                                    if comp_cabecalhotcp \
    <= 9520:
                                                                        return 'web'
                                                                    elif comp_cabecalhotcp \
    > 9520:
                                                                        if comp_cabecalhotcp \
    <= 11916:
                                                                            return 'p2p'
                                                                        elif comp_cabecalhotcp \
    > 11916:
                                                                            return 'web'
                                                        elif TamanhoJanela \
    > 1457064:
                                                            if CompPacoteIp \
    <= 63801:
                                                                return 'web'
                                                            elif CompPacoteIp \
    > 63801:
                                                                return 'ftp'
                                            elif TamanhoJanela \
    > 3509958:
                                                if CompPacoteIp \
    <= 69032:
                                                    return 'p2p'
                                                elif CompPacoteIp \
    > 69032:
                                                    if TamanhoJanela \
    <= 7299764:
                                                        return 'web'
                                                    elif TamanhoJanela \
    > 7299764:
                                                        return 'p2p'
                                        elif TamanhoPayload > 151772:
                                            if TamanhoJanela <= 1773867:
                                                return 'web'
                                            elif TamanhoJanela \
    > 1773867:
                                                if comp_cabecalhotcp \
    <= 11830:
                                                    return 'ftp'
                                                elif comp_cabecalhotcp \
    > 11830:
                                                    if TamanhoPayload \
    <= 215927:
                                                        return 'web'
                                                    elif TamanhoPayload \
    > 215927:
                                                        return 'ftp'
                                    elif comp_cabecalhotcp > 16008:
                                        if TamanhoJanela <= 11615977:
                                            if TamanhoJanela <= 1549788:
                                                return 'p2p'
                                            elif TamanhoJanela \
    > 1549788:
                                                if CompPacoteIp \
    <= 3678517:
                                                    return 'web'
                                                elif CompPacoteIp \
    > 3678517:
                                                    return 'p2p'
                                        elif TamanhoJanela > 11615977:
                                            return 'ftp'
            elif TamanhoJanela > 12945544:
                if TamanhoPayload <= 1179951:
                    if CompPacoteIp <= 1094127:
                        if TamanhoJanela <= 22425083:
                            if TamanhoJanela <= 19075583:
                                return 'p2p'
                            elif TamanhoJanela > 19075583:
                                return 'web'
                        elif TamanhoJanela > 22425083:
                            return 'p2p'
                    elif CompPacoteIp > 1094127:
                        return 'ftp'
                elif TamanhoPayload > 1179951:
                    return 'ftp'