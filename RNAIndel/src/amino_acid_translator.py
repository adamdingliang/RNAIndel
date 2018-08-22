#!/usr/bin/env python3

def tranlate_seq(seq):
    """translate
    """
    codon_table = {
                   'TTT':'F', 'TTC':'F', 'TTA':'L', 'TTG':'L',
                   'CTT':'L', 'CTC':'L', 'CTA':'L', 'CTG':'L',
                   'ATT':'I', 'ATC':'I', 'ATA':'I', 'ATG':'M',
                   'GTT':'V', 'GTC':'V', 'GTA':'V', 'GTG':'V',
                   'TCT':'S', 'TCC':'S', 'TCA':'S', 'TCG':'S',
                   'CCT':'P', 'CCC':'P', 'CCA':'P', 'CCG':'P',
                   'ACT':'T', 'ACC':'T', 'ACA':'T', 'ACG':'T',
                   'GCT':'A', 'GCC':'A', 'GCA':'A', 'GCG':'A',
                   'TAT':'Y', 'TAC':'Y', 'TAA':'*', 'TAG':'*',
                   'CAT':'H', 'CAC':'H', 'CAA':'Q', 'CAG':'Q',
                   'AAT':'N', 'AAC':'N', 'AAA':'K', 'AAG':'K',
                   'GAT':'D', 'GAC':'D', 'GAA':'E', 'GAG':'E',
                   'TGT':'C', 'TGC':'C', 'TGA':'*', 'TGG':'W',
                   'CGT':'R', 'CGC':'R', 'CGA':'R', 'CGG':'R',
                   'AGT':'S', 'AGC':'S', 'AGA':'R', 'AGG':'R',
                   'GGT':'G', 'GGC':'G', 'GGA':'G', 'GGG':'G'
                  }
    
    peptide = ''
    codon_length = 3
    for i in range(0, len(seq)-codon_length+1, codon_length):
        peptide += codon_table[seq[i:(i+codon_length)]]
    
    return peptide

seq = 'ATG CAG ATG GCG ACT T'
print(tranlate_seq(seq))
