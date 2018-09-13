#!/usr/bin/env python3
"""
9th step (last) of analysis

Output analysis result in .vcf
 
'indel_vcf_writer' is the main routine in this module

Must hard-code define_info_dict and define_format_dict
to edit the meta info.
"""
import re
import pysam
import datetime
import pandas as pd
from functools import partial
from .indel_vcf import IndelVcfReport
from .left_aligner import peek_left_base

metaID = re.compile(r'ID=([A-Za-z]+)')

def indel_vcf_writer(df, bam, fasta, vcfname):
    """Output result in .vcf
    
    Args:
        df (pandas.DataFrame): assumed to be sorted and left-aligned
        bam (str): path to bam
        fasta (str): path to fasta
        vcfname (str): output vcf name
    Returns:
        None: a vcf file will be written out
    """
    fa = pysam.FastaFile(fasta)
    
    info = define_info_dict()
    fmt = define_format_dict()
    vcf = partial(generate_indel_vcf, info_dict=info, format_dict=fmt, fa=fa)

    df['vcf'] = df.apply(vcf, axis=1)
    vcf_records = df.apply(lambda x: x['vcf'].vcf_record, axis=1).values
    
    with open(vcfname, 'w') as f:
        f.write(vcf_template(bam, info, fmt) + '\n')
        f.write('\n'.join(vcf_records))


def generate_indel_vcf(row, info_dict, format_dict, fa):
    """Converts Bambino format to VCF format and 
    populate meta info

    Args:
        row (pandas.Series): each row represents an indel
        info_dict (dict): generated by define_info_dict()
        format_dict (dict): generated by define_format_dict()
        fa (pysam.FastFile): obj. storing the refernce info
    """
    idl_vcf = \
    IndelVcfReport(fa, row['chr'], row['pos'], row['ref'], row['alt'])
    
    # dbSNP ID
    idl_vcf.ID = row['dbsnp']
    
    # reclassification info if applicable
    try:
        idl_vcf.FILTER = row['filter']
    except:
        pass
    
    # fill INFO field
    info = link_datadict_to_dataframe(row, info_dict)
    idl_vcf.INFO = info

    # fill FORMAT field
    format = link_datadict_to_dataframe(row, format_dict)
    idl_vcf.FORMAT = format
    
    return idl_vcf


def link_datadict_to_dataframe(row, dict):
    """Match column name and acutal data in dataframe
    
    Args:
        row (pandas.Series)
        dict (dict): info_dict or format_dict
    Returns:
        d (dict): {'meta_info_ID: row['column_name']}
    """
    d = {}
    for k, v in dict.items():
        d[k] = [row[c] for c in v['COLUMN']]
        if len(d[k]) == 1:
            d[k] = d[k][0]

    return d


def get_today():
    """Get today's date

    Args:
        None
    Returns:
        today (str): yyyymmdd
    """
    dt = datetime.datetime.now()
    today = str(dt.year)+str(dt.month)+str(dt.day)
    
    return today 


def get_samplename(bam):
    """Get sample name

    Args:
        bam (str): path to bam
    Returns:
        samplename (str): as found in bam file
                          or 'SampleName' if not found
    """
    try:
        bamheader = pysam.AlignmentFile(bam).header
        samplename = bamheader['RG'][0]['SM']
    except:
        samplename = 'SampleName'
        
    return samplename


def vcf_template(bam, info_dict, format_dict):
    """Prepare VCF meta info lines and header lines 
    https://samtools.github.io/hts-specs/VCFv4.2.pdf
  
   Args:
       bam (str): path to bam
       info_dict (dict): generated by define_info_dict()
       format_dict (dict): generated by define_format_dict()
   Returns:
       template (str): representing VCF template
   """
    meta_1 = \
    [
     '##fileformat=VCFv4.2', 
     '##filedate='+get_today(), 
     '##source=RNAIndel',
     '##reference=GRCh38',
     '##FILTER=<ID=reclassified,Description="Reclassified by user-defined panel">'
    ]
     
    info_order = ['PRED', 'PROB', 'DB', 'ANNO', 'MAXMAF', 'COMMON',\
                  'CLIN', 'ICP', 'DSM', 'ISZ', 'REP', 'UQM',\
                  'NEB', 'BID', 'MTA', 'TRC', 'NMD',\
                  'IPG', 'LSG', 'ATI', 'ATD']

    meta_2 = ['##INFO=<ID='+i+','\
              'Number='+info_dict[i]['Number']+','\
              'Type='+info_dict[i]['Type']+','\
              'Description="'+info_dict[i]['Description']+'">'\
               for i in info_order] 
    
    format_order = ['AD']

    meta_3 = ['##FORMAT=<ID='+i+','\
              'Number='+format_dict[i]['Number']+','\
              'Type='+format_dict[i]['Type']+','\
              'Description="'+format_dict[i]['Description']+'">'\
               for i in format_order] 
    
    meta = meta_1 + meta_2 + meta_3
     
    header = \
    [
     '#CHROM',
     'POS',
     'ID',
     'REF',
     'ALT',
     'QUAL',
     'FILTER',
     'INFO',
     'FORMAT',
     get_samplename(bam)
    ]    
    
    template = '\n'.join(meta  + ['\t'.join(header)])

    return template

def define_info_dict():
    """Define INFO field in dict

    Args:
       None
    Returns:  
       d (dict): dict of dict. The first dict's key is 
                 INFO ID (see VCF spec.). The value of 
                 'COLUMN' in the nested dict is a list.
       
                d=  {
                     'INFO_ID'{
                               'COLUMN':['column name in df']
                               'Number':'see VCF spec'
                               'Type':'see VCF spec'
                               'Description':'describe this INFO'
                              },
                     'INFO_ID'{
                                ....
                              }
                    }
    """
    d = {
         'PRED':{
                 'COLUMN':['predicted_class'], 
                 'Number':'1', 
                 'Type':'String', 
                 'Description':'Predicted class: somatic, germline, artifact'
                 },
         'PROB':{
                 'COLUMN':['prob_s', 'prob_g', 'prob_a'], 
                 'Number':'3', 
                 'Type':'Float', 
                 'Description':'Prediction probability of '
                               'being somatic, germline, artifact in this order'
                },
         'DB':{
               'COLUMN':['dbsnp'],
               'Number':'0',
               'Type':'Flag',
               'Description':'Flagged if on dbSNP'
               },
         'ANNO':{
                 'COLUMN':['annotation'],
                 'Number':'.',
                 'Type':'String',
                 'Description':'Indel annotation in '
                               'GeneSymbol|RefSeqAccession|CodonPos|IndelEffect. '
                               'Delimited by comma for multiple isoforms'
                },
         'MAXMAF':{
                   'COLUMN':['max_maf'],
                   'Number':'1',
                   'Type':'Float',
                   'Description':'Maximum minor allele frequency (MAF) '
                                 'reported in dbSNP or ClinVar'
                   },
         'COMMON':{
                   'COLUMN':['is_common'],
                   'Number':'0',
                   'Type':'Flag',
                   'Description':'Flagged if curated Common on dbSNP or MAXMAF > 0.01'
                  },
         'CLIN':{
                 'COLUMN':['clin_info'],
                 'Number':'1',
                 'Type':'String',
                 'Description':'Clinical Significance|Condition curated in ClinVar'
                },
         'ICP':{
                'COLUMN':['indel_complexity'],
                'Number':'1',
                'Type':'Integer',
                'Description':'Indel complexity'
               },
         'DSM':{
                'COLUMN':['dissimilarity'],
                'Number':'1',
                'Type':'Float',
                'Description':'Dissimilarity',
               },
         'ISZ':{
                'COLUMN':['indel_size'],
                'Number':'1',
                'Type':'Integer',
                'Description':'Indel size'
               },
         'REP':{
                'COLUMN':['repeat'],
                'Number':'1',
                'Type':'Integer',
                'Description':'Repeat'
               },
         'UQM':{
                'COLUMN':['is_uniq_mapped'],
                'Number':'0',
                'Type':'Flag',
                'Description':'Flagged if supported by uniquely mapped reads'
               },
         'NEB':{
                'COLUMN':['is_near_boundary'],
                'Number':'0',
                'Type':'Flag',
                'Description':'Flagged if near exon boundary'
               },
         'BID':{
                'COLUMN':['is_bidirectional'],
                'Number':'0',
                'Type':'Flag',
                'Description':'Flagged if supported by forward and reverse reads'
               },    
         'MTA':{
                'COLUMN':['is_multiallelic'],
                'Number':'0',
                'Type':'Flag',
                'Description':'Flagged if multialleleic'
               }, 
         'TRC':{
                'COLUMN':['is_truncating'],
                'Number':'0',
                'Type':'Flag',
                'Description':'Flagged if truncating indel'
               },
         'NMD':{
                'COLUMN':['is_nmd_insensitive'],
                'Number':'0',
                'Type':'Flag',
                'Description':'Flagged if insensitive to nonsense mediated decay'
               },
         'IPG':{
                'COLUMN':['ipg'],
                'Number':'1',
                'Type':'Float',
                'Description':'Indels per gene'
               },
         'LSG':{
                'COLUMN':['local_strength'],
                'Number':'1',
                'Type':'Float',
                'Description':'Local strength of nucleotide sequence'
               },
         'ATI':{
                'COLUMN':['is_at_ins'],
                'Number':'0',
                'Type':'Flag',
                'Description':'Flagged if insertion of A or T'
               },
         'ATD':{
                'COLUMN':['is_at_del'],
                'Number':'0',
                'Type':'Flag',
                'Description':'Flagged if deletion of A or T'
               }
        }
  
    return d

def define_format_dict():
    """Define FORMAT field
    Args: 
        None
    Returns:
        d (dict): see define_info_dict 
    """
    d = {
         'AD':{
               'COLUMN':['ref_count', 'alt_count'],
               'Number':'R',
               'Type':'Integer',
               'Description':'Allelic depths by fragment (not read) '
                             'for the ref and alt alleles in the order listed'
              }
        }
        
    return d   
