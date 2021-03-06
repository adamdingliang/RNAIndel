# Run Example
Here, we demonstrate an analysis example using sample data prepared from the Jurkat T-cell leukemia cell line.<br>
This cell line harbors two known indels in the *PTEN* tumor suppressor gene: a 2-nt deletion followed by a 9-nt insertion at codon 234 and a 39-nt insertion at codon 246 (Figure 2 in [Reference](#reference)). 
We apply the RNAIndel pipeline to a sample BAM file ([sample.bam](./inputs/sample.bam)), which contains the GRCh38 region chr10:80,000,000-90,000,000 (the *PTEN* locus is chr10:87,863,113-87,971,930). 

## Setup
We assume RNAIndel is [installed](../README.md#installation).<br>
**Step 1:** Download the sample dataset.
```
git clone https://github.com/stjude/RNAIndel.git 

RNAIndel
     |_ rnaindel
     ...
     |_ sample_data <------ sample dataset (GRCh38) 
     ...
```
**Step 2:**  Download and unpack [data_dir_38.tar.gz](http://ftp.stjude.org/pub/software/RNAIndel/data_dir_38.tar.gz).  
```
RNAIndel
    |_ rnaindel
    ...
    |_ sample_data
    ...
    |_ data_dir_38 <--- Unpacked here for demo. 
    ...
```

## Perform analysis

### Working with the built-in Bambino caller
```
$ rnaindel  -b ./sample_data/inputs/sample.bam \
            -o ./sample_data/outputs/sample.vcf \
            -f path/to/your_GRCh38.fa \
            -d ./data_dir_38

indel calling completed successfully. # indel calling by the built-in caller is done.
rnaindel completed successfully.      # all steps done. 
```
Fifteen coding indels are reported in the ouput [VCF](./outputs/sample.vcf) file: 2 somatic, 1 germline, and 12 artifact indels (see INFO field).
The two *PTEN* indels are predicted as somatic. The first indel is a complex indel in which a 2-nt deletion and a 9-nt insertion 
are involved. This indel is detected as a 7-nt insertion at codon 233 with indel complexity = 2 (See INFO field in [VCF](./outputs/sample.vcf)). The second indel
is detected as a 7-nt insertion at codon 246, not as a 39-nt insertion, due to the soft-clipped alignment. 

### Working with GATK-HaplotypeCaller 
The sample BAM file was preprocessed following GATK RNA-Seq Variant Calling [BestPractice](https://software.broadinstitute.org/gatk/documentation/article.php?id=3891). 
GATK-HC (ver 4.0.2.1) called variants in the preprocessed BAM file ([sample.gatk.bam](./inputs/sample.gatk.bam)) and 
generated a [VCF](./inputs/sample_gatk.vcf) file.Now, the indels in the GATK VCF file are classified. **Please input the original BAM file (sample.bam), not the preprocessed one (sample.gatk.bam)**.
```
$ rnaindel -b ./sample_data/inputs/sample.bam \
           -c ./sample_data/inputs/sample_gatk.vcf \
           -o ./sample_data/outputs/sample_gatk_classified.vcf \
           -f path/to/your_GRCh38.fa \
           -d ./data_dir_38

rnaindel completed successfully. # all steps done (indel calling by the built-in caller is not performed)
```
Four coding indels are reported in the output [VCF](./outputs/sample_gatk_classified.vcf) file: 2 somatic, 1 germline, and 1 artifact. 
Both *PTEN* indels are predicated as somatic. The 39-nt insertion at codon 246 is also detected as a 7-nt insertion by GATK-HC. 
However, the indel at codon 234 is detected as a combination of two insertions: 
the GGCCC insertion at chr10:87957916 and the TG insertion at chr10:87957917. In the output [VCF](./outputs/sample_gatk_classified.vcf), 
these two are annotated as "RQB=chr10:87957916:G:GGGCCCAT". This means that RNAIndel could not find these two indels in the BAM 
file as specified by the input [VCF](./inputs/sample_gatk.vcf) file and, instead, found the GGCCCAT insertion at chr10:87957916 in the BAM file and 
used this for prediction. 

## Reference
Shan, X, Czar, J.C., Bunnell, S.C., Liu, P., Liu, Y., Schwartzberg, P.L., Wange, R.L. (2000) Deficiency of PTEN in Jurkat T Cells Causes Constitutive Localization of Itk to the Plasma Membrane and Hyperresponsiveness to CD3 Stimulation. Mol Cell Biol., 20: 6945–6957. PMID [10958690](https://www.ncbi.nlm.nih.gov/pubmed/10958690)      
