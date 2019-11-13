#!/bin/bash

#set -x
set -e
#set -u

usage()
{
cat <<EOF >&2
${txtcyn}
Usage:

$0 options${txtrst}

${bldblu}Function${txtrst}:

This script is used to perform DE gene analysis using DESeq2.

It requires at least two input files.

The count file (normally generated using ${txtred}HTseq-count${txtrst} and multiple
samples are pasted using ${txtred}pasteMultipleFilesSpecialCol.py${txtrst}):

#--------FILE content-----------------------------
ID	A_1	A_2	A_3	B_1	B_2	C_1	C_2	...
a	1	1	1	2	2	3	3	...
b	1	1	1	2	2	3	3	...
c	1	1	1	2	2	3	3	...
d	1	1	1	2	2	3	3	...
e	1	1	1	2	2	3	3	...
#--------FILE content-----------------------------

The sample file (with the first column as the colnames of countfile
and second column indicates the origin of each replicates.)

#--------FILE content------------------------------
#---the formula should be <conditions> which is the default
Sample	conditions
A_1	A
A_2	A
A_3	A
B_1	B
B_2	B
C_1	C
C_2	C
#--------FILE content-----------------------------
#--------FILE content--multiple columns are allowed-------------
#--------One <conditions> column is needed----------------------
#---the formula should be <cell+time+cell:time> 
#---the reduced formula (only applicable in <time-series>) 
#---should be  <cell+time> or <cell> or <time> for
#---specific purposes
#---First appeared sample will be treated as control.
Sample	conditions	cell	time
A_1_1	A_1	A	1	
A_1_2	A_1	A	1
A_1_3	A_1	A	1
A_2_1	A_2	A	2	
A_2_2	A_2	A	2
A_2_3	A_2	A	2
B_1_1	B_1	B	1	
B_1_2	B_1	B	1
B_1_3	B_1	B	1
B_2_1	B_2	B	2	
B_2_2	B_2	B	2
B_2_3	B_2	B	2
#--------FILE content-----------------------------

Optional file to specify the comparasion patterns you want to do


#--------FILE content- for pairwise compare-------
A	B
A	C
B	C
#--------FILE content-----------------------------

#--------FILE content- for one control-------
A	C
B	C
#--------FILE content-----------------------------

${txtbld}OPTIONS${txtrst}:
	-f	Data file ${bldred}[A gene count matrix, NECESSARY]
		CHECK ABOVE FOR DETAILS
		${txtrst}
	-s	Sample file ${bldred}[A multiple columns file with header line, 
		For <timeseries>,  one <conditions> columns is needed.
		NECESSARY]
		CHECK ABOVE FOR DETAILS
		${txtrst}
	-d	The design formula for DESeqDataSetFromMatrix.
		${bldred}[Default <conditions>, 
		accept <cell+time+cell:time> for example 2.]
		${txtrst}
	-D	The reduced design formula for DESeq.
		${bldred}[Only applicable to <timeseries> analysis, 
		accept <cell+time> or <time> or <cell> for example 2.]
		${txtrst}
	-m	Specify the comparasion mode.
		${bldred}[Default <pairwise>, accept <timeseries>,
		<pairwise> comparasion will still be done in <timeseries>
		mode.
		NECESSARY]
		${txtrst}
	-p	A file containing the pairs needed to do comparasion. 
		CHECK ABOVE FOR DETAILS
		All samples will be compared in <pairwise> mode if not specified here.
	
	-F	Log2 Fold change for screening DE genes.
		${bldred}Default 1${txtrst}

	-P	FDR for screening DE genes.
		${bldred}Default 0.01${txtrst}

	-q	FDR for screening time-series DE genes.
		${bldred}Default 0.1${txtrst}

	-e	Execute programs
		${bldred}Default TRUE${txtrst}

	-i	Install packages of not exist. 
		${bldred}Default FALSE${txtrst}

Eg.
	$0 -f matirx -s sample 
	$0 -f matirx -s sample -p compare_pair

EOF
}

file=
sample=
formula="conditions"
reducedFormula=
compare_mode='pairwise'
compare_pair='FALSE'
header='TRUE'
ist='FALSE'
execute='TRUE'
#outputdir='./'
fdr=0.01
log2fc=1
t_fdr=0.1

while getopts "hd:D:e:f:F:i:m:o:p:P:q:s:" OPTION
do
	case $OPTION in
		h)
			usage
			exit 1
			;;
		d)
			formula=$OPTARG
			;;
		D)
			reducedFormula=$OPTARG
			;;
		e)
			execute=$OPTARG
			;;
		f)
			file=$OPTARG
			;;
		F)
			log2fc=$OPTARG
			;;
		i)
			ist=$OPTARG
			;;
		m)
			compare_mode=$OPTARG
			;;
		o)
			outputdir=$OPTARG
			;;
		p)
			compare_pair=$OPTARG
			;;
		P)
			fdr=$OPTARG
			;;
		q)
			t_fdr=$OPTARG
			;;
		s)
			sample=$OPTARG
			;;
		?)
			usage
			exit 1
			;;
	esac
done

if [ -z $file ]; then
	usage
	exit 1
fi

mid=".DESeq2"

formulaV=`echo ${formula} | sed 's/ //g' | awk '{a=split($1,b,"+"); c="\""b[1]"\""; for (i=2;i<=a;i++) if (b[i] !~/:/) c=c",""\""b[i]"\""; print c;}'`
color_v=`echo ${formula} | sed 's/ //g' | cut -d ':' -f 1 | cut -d '+' -f 1`
shape_v=`echo ${formula} | sed 's/ //g' | cut -d ':' -f 1 | cut -d '+' -f 2`

#formulaS=`echo ${formula} | sed 's/ //g' | awk '{a=split($1,b,"+"); c=b[1]; for (i=2;i<=a;i++) c=c":"b[i]; print $1"+"c;}'`

cat <<END >${file}${mid}.r

if ($ist){
	source("https://bioconductor.org/biocLite.R")
	source(pipe(paste("wget -O -", URL)))
	biocLite("DESeq2")
}

library(DESeq2)
library("RColorBrewer")
library("gplots")
library("amap")
library("ggplot2")

data <- read.table("${file}", header=T, row.names=1, com='', quote='',
	check.names=F, sep="\t")

data <- data[rowSums(data)>1,]

sample <- read.table("${sample}", header=T, row.names=1, com='',
	quote='', check.names=F, sep="\t", colClasses="factor")

sample <- data.frame(lapply(sample, function(x) factor(x, levels=unique(x))))
#paste0(sample \$cell, sample\$time)

if ("${compare_mode}" == "pairwise") {
	print("Perform pairwise comparasion using <design=~${formula}>")
	ddsFullCountTable <- DESeqDataSetFromMatrix(countData = data,
		colData = sample,  design= ~ ${formula})
} else if ("${compare_mode}" == "timeseries") {
	print("Perform pairwise comparasion using <design=~conditions>")
	ddsFullCountTable <- DESeqDataSetFromMatrix(countData = data,
		colData = sample,  design= ~conditions)
}

dds <- DESeq(ddsFullCountTable)

# Get normalized counts

print("Output normalized counts")
normalized_counts <- counts(dds, normalized=TRUE)

write.table(normalized_counts, file="${file}${mid}.normalized.xls",
quote=F, sep="\t", row.names=T, col.names=T)
system(paste("sed -i '1 s/^/ID\t/'", "${file}${mid}.normalized.xls"))

rld <- rlog(dds)
vsd <- varianceStabilizingTransformation(dds)
rlogMat <- assay(rld)
vstMat <- assay(vsd)

print("Output rlog transformed normalized ocunts")
write.table(rlogMat, file="${file}${mid}.normalized.rlog.xls",
quote=F, sep="\t", row.names=T, col.names=T)
system(paste("sed -i '1 s/^/ID\t/'", "${file}${mid}.normalized.rlog.xls"))

print("Output vst transformed normalized ocunts")
write.table(vstMat, file="${file}${mid}.normalized.vst.xls",
quote=F, sep="\t", row.names=T, col.names=T)
system(paste("sed -i '1 s/^/ID\t/'", "${file}${mid}.normalized.vst.xls"))

print("Performing sample clustering")
hmcol <- colorRampPalette(brewer.pal(9, "GnBu"))(100)
pearson_cor <- as.matrix(cor(rlogMat, method="pearson"))
hc <- hcluster(t(rlogMat), method="pearson")

svg(filename="${file}${mid}.normalized.rlog.pearson.svg", pointsize=10)
heatmap.2(pearson_cor, Rowv=as.dendrogram(hc), symm=T, trace="none",
col=hmcol, margins=c(11,11), main="The pearson correlation of each
sample")
dev.off()


# Begin DE-gene compare

de_twosample <- function
(
dds, 
sampleV
){
	#print(sampleV)
	sampleA <- as.vector(sampleV\$sampA)
	sampleB <- as.vector(sampleV\$sampB)
	print(paste("DE genes between", sampleA, sampleB, sep=" "))
	contrastV <- c("conditions", sampleA, sampleB)
	res <- results(dds,  contrast=contrastV)
	baseA <- counts(dds, normalized=TRUE)[, colData(dds)\$condition == sampleA]
	baseMeanA <- as.data.frame(rowMeans(baseA))
	colnames(baseMeanA) <- sampleA
	baseB <- counts(dds, normalized=TRUE)[, colData(dds)\$condition == sampleB]
	baseMeanB <- as.data.frame(rowMeans(baseB))
	colnames(baseMeanB) <- sampleB
	res <- cbind(baseMeanA, baseMeanB, as.data.frame(res))
	res <- cbind(ID=rownames(res), as.data.frame(res))
	res\$baseMean <- rowMeans(cbind(baseA, baseB))
	res\$padj[is.na(res\$padj)] <- 1
	file_base <- paste("${file}${mid}", sampleA, "_vs_", sampleB,"results", sep=".")
	write.table(as.data.frame(res), file=file_base, sep="\t", quote=F, row.names=F)
	
	res_de <- subset(res, res\$padj<${fdr}, select=c('ID', sampleA,
		sampleB, 'log2FoldChange', 'padj'))
	res_de_up <- subset(res_de, res_de\$log2FoldChange>=${log2fc})
	file <- paste(file_base, "DE_up", sep=".")
	write.table(as.data.frame(res_de_up), file=file, sep="\t", quote=F, row.names=F)
	res_de_up_id <- subset(res_de_up, select=c("ID"))
	file <- paste(file_base, "DE_up_id", sep=".")
	write.table(as.data.frame(res_de_up_id), file=file, sep="\t", 
		quote=F, row.names=F, col.names=F)
	
	res_de_dw <- subset(res_de, res_de\$log2FoldChange<=(-1)*${log2fc})
	file <- paste(file_base, "DE_dw", sep=".")
	write.table(as.data.frame(res_de_dw), file=file, sep="\t", quote=F, row.names=F)
	res_de_dw_id <- subset(res_de_dw, select=c("ID"))
	file <- paste(file_base, "DE_dw_id", sep=".")
	write.table(as.data.frame(res_de_dw_id), file=file, sep="\t", 
		quote=F, row.names=F, col.names=F)

	logCounts <- log2(res\$baseMean+1)
	logFC <- res\$log2FoldChange
	FDR <- res\$padj
	svg(filename=paste(file_base, "MA.svg", sep="."))
	plot(logCounts, logFC, col=ifelse(FDR<=0.01, "red", "black"),
	xlab="logCounts", ylab="logFC", main="MA plot", pch='.')
	dev.off()
	svg(filename=paste(file_base, "Volcano.svg", sep="."))
	plot(logFC, -1*log10(FDR), col=ifelse(FDR<=0.01, "red", "black"),
	xlab="logFC", ylab="-1*log1o(FDR)", main="Volcano plot", pch=".")
	dev.off()
}



de_timeseries <- function
(
dds, 
sampleV
){
	print(paste("Time series DE genes", sampleV, sep=" "))
	contrastV <- list(sampleV)
	res <- results(dds,  contrast=contrastV, test="Wald")
	res\$padj[is.na(res\$padj)] <- 1
	res <- cbind(ID=rownames(res), as.data.frame(res))
	res <- subset(res, select=c('ID', 'log2FoldChange', 'padj'))

	file_base <- paste("${file}${mid}", paste0(sampleV, collapse="__"),"results", sep=".")
	write.table(as.data.frame(res), file=file_base, sep="\t", quote=F, row.names=F)
	
	res_de <- subset(res, res\$padj<${t_fdr}, select=c('ID','log2FoldChange','padj'))
	res_de_up <- subset(res_de, res_de\$log2FoldChange>=${log2fc})
	file <- paste(file_base, "DE_up", sep=".")
	write.table(as.data.frame(res_de_up), file=file, sep="\t", quote=F, row.names=F)
	res_de_up_id <- subset(res_de_up, select=c("ID"))
	file <- paste(file_base, "DE_up_id", sep=".")
	write.table(as.data.frame(res_de_up_id), file=file, sep="\t", 
		quote=F, row.names=F, col.names=F)
	
	res_de_dw <- subset(res_de, res_de\$log2FoldChange<=(-1)*${log2fc})
	file <- paste(file_base, "DE_dw", sep=".")
	write.table(as.data.frame(res_de_dw), file=file, sep="\t", quote=F, row.names=F)
	res_de_dw_id <- subset(res_de_dw, select=c("ID"))
	file <- paste(file_base, "DE_dw_id", sep=".")
	write.table(as.data.frame(res_de_dw_id), file=file, sep="\t", 
		quote=F, row.names=F, col.names=F)

	logFC <- res\$log2FoldChange
	FDR <- res\$padj
	svg(filename=paste(file_base, "Volcano.svg", sep="."))
	plot(logFC, -1*log10(FDR), col=ifelse(FDR<=0.01, "red", "black"),
	xlab="logFC", ylab="-1*log1o(FDR)", main="Volcano plot", pch=".")
	dev.off()
}

if ("${compare_mode}" == "pairwise" || "${compare_mode}" == "timeseries") {
	if ("${compare_pair}" == "FALSE") {
		compare_data <- as.vector(unique(sample\$conditions))
		#compare_combine <- as.matrix(combn(compare_data, 2))
		#for(i in compare_combine) {
		#	de_twosample(dds, i)
		#}
		len_compare_data <- length(compare_data)
		for(i in 1:(len_compare_data-1)) {
			for(j in (i+1):len_compare_data) {
				tmp_compare <- as.data.frame(
					cbind(sampA=compare_data[i],
					sampB=compare_data[j]))
				de_twosample(dds, tmp_compare)
			}
		}
	}else {
		compare_data <- read.table("${compare_pair}", sep="\t",
		check.names=F, quote='', com='')
		colnames(compare_data) <- c("sampA", "sampB")
		by(compare_data, 1:nrow(compare_data), function (x)
		de_twosample(dds, x))
	}	
}
	
if ("${compare_mode}" == "timeseries") {
	# Check the following links for time-serise reference
	# http://www.bioconductor.org/help/workflows/rnaseqGene/#count
	# https://support.bioconductor.org/p/65676/#66860
	# https://support.bioconductor.org/p/62357/#62368
	print("Performing timeseries analysis using <design=~${formula}")
	ddsFullCountTable <- DESeqDataSetFromMatrix(countData = data,
		colData = sample,  design= ~ ${formula})

	# The following chunk performs a likelihood ratio test,  where we
	# remove the strain-specific differences over time. Genes with
	# small p values from this test are those which,  at one or more
	# time points after time 0 showed a strain-specific effect. Note
	# therefore that this will not give small p values to genes which
	# moved up or down over time in the same way in both strains.

	dds <- DESeq(ddsFullCountTable, test="LRT", reduced=~${reducedFormula})
	compareP <- resultsNames(dds)
	
	strain_specific <- compareP[grepl("\\\\.", compareP)]
	
	lapply(strain_specific, function(x) de_timeseries(dds, as.vector(x)))

	# results(dds, name=strainmut.minute60):
	# 	it is an interaction term because it contains the names of
	# 	both variables strain and minute. 
	#	So this term is a test for if the mut vs WT fold change is
	# 	different at minute 60 than at minute 0. 

	# results(dds, name="minute_60_vs_0")
	#	To generate the tables of log fold change of 60 minutes vs 0
	#   minutes for the WT strain would be:
	
	# results(dds, contrast=list(c("minute_60_vs_0", "strainmut.minute60")))
	#	To generate the tables of log fold change of 60 minutes vs 0
	#	minutes for the mut strain would be the sum of the WT term
	#	above and the interaction term which is an additional effect
	#	beyond the effect for the reference level (WT)

	rld <- rlog(dds)
}


print("PCA analysis")
formulaV <- c(${formulaV})
pca_data <- plotPCA(rld, intgroup=formulaV, returnData=T)
percentVar <- round(100 * attr(pca_data, "percentVar"))
svg(filename="${file}${mid}.normalized.rlog.pca.svg", pointsize=10)
if (length(formulaV)==1) {
  p <- ggplot(pca_data, aes(PC1, PC2, color=${color_v}))
} else if (length(formulaV==2)) {
  p <- ggplot(pca_data, aes(PC1, PC2, color=${color_v},
  shape=${shape_v}))
}
p + geom_point(size=3) + 
	xlab(paste0("PC1: ", percentVar[1], "% variance")) +
	ylab(paste0("PC2: ", percentVar[2], "% variance"))
#plotPCA(rld, intgroup=c(${formulaV}))
dev.off()


END

if test "${execute}" == "TRUE";
then
	Rscript ${file}${mid}.r
fi
