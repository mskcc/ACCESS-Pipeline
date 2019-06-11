#!/ifs/opt/bin/Rscript

########################
# Loess normalize target exon coverage based on GC content.
# Modified from IMPACT solid pipeline to support cfDNA analysis
#ptashkir@mskcc.org 09 December 2018
# Changes:
# - seperate panel A from panel B targets
# submit as
# R --slave --vanilla --args <prefix> <outdir> <target file with GC> <interval coverage-file> <"tumor|"normal">
########################

# R --slave --vanilla --args <prefix> <_ALL_intervalcoverage.txt> <gc_percent-file>
library(dplyr)
rm(list=ls(all=T));


source("/dmp/resources/prod/tools/bio/misc/textplot.R")
args = commandArgs(trailingOnly=TRUE)
print(args)
prefix <- args[1];
outdir <- args[2];
gcfile <- args[3];   # Example: "v4_hg19_all_GC200bp.txt";
interval_file <- args[4];
type <-args[5];


tar = read.delim(gcfile,sep="\t",header=T,as.is=T,fill=T)

#colnames(tar) = c("Chrom", "Start", "End", "Strand", "Target", "GC_150bp", "GC_Interval","Gene","Cyt","GeneExon")
tar$Chr = paste("chr", tar$Chrom, sep = "")
#tar$Interval = paste(tar$Chrom, (tar$Start+1), sep = ":")
#tar$Interval = paste(tar$Interval, (tar$End), sep = "-")
tar$Order = row.names(tar)

d = read.delim(interval_file,sep="\t",header=T,as.is=T,fill=T)
d$Interval = d$Target
d$Order = row.names(d)
columnsKeep =  c("Order","Interval",colnames(d)[grep("_mean_cvg",colnames(d))])
d = d[,columnsKeep]


tiling.probes <- tar[grep("panel_B", tar$Target),'Interval'];

outtablename <- file.path(outdir,paste(prefix,"_",type,"_ALL_intervalnomapqcoverage_loess.txt",sep=""));
#tar <- read.delim(gcfile,sep="\t",header=T,as.is=T,fill=T);

cat(dim(tar),"\t",dim(d),"\n");

#Order by target
chrom <- c(seq(1,22,1),'X','Y');
order.genomic <- function(dat){
	chr.pos <- do.call('rbind',lapply(dat[,'Interval'], function(x){
		f <- unlist(strsplit(x,'\\:'));
		g <- unlist(strsplit(f[2],'\\-'));
		return(c('chr0'=f[1],'pos0'=g[1]));
	}));
	dat <- cbind(dat,chr.pos);
	ret <- do.call('rbind',lapply(chrom,function(chr.i){
		dat. <- dat[which(dat[,'chr0'] == chr.i),];
		dat. <- dat.[order(as.numeric(as.character(dat.[,'pos0'])),decreasing=F),];
		return(dat.);
	}));
	return(ret[,-c(ncol(ret)-1,ncol(ret))]);
}
tar.sort <- order.genomic(tar);
d.sort <- order.genomic(d);

cat(dim(tar.sort),"\n");
cat(dim(d),"\n");
cat(dim(d.sort),"\n");

a <- tar.sort[,'Interval'] != d.sort[,'Interval'];
cat("Match test1 ",sum(a)," ",dim(tar.sort)," ",dim(d.sort),"\n");


targets <- tar.sort[which(!(tar.sort[,'Chr'] %in% c('chrY'))),];
gc2 <- d.sort[match(targets[,'Interval'],d.sort[,'Interval']),];


cat(gc2[1:10,'Interval'],"\n");
cat(targets[1:10,'Interval'],"\n");
cat(dim(gc2),"\n");
cat(dim(targets),"\n");
a <- gc2[,'Interval'] != targets[,'Interval'];
cat("Match test2  ",sum(a)," ",dim(gc2)," ",dim(targets),"\n");

index <- which(is.na(gc2[,'Interval']));
cat(length(index),"\n");
index2 <- which(is.na(targets[,'Interval']));
cat(length(index2),"\n");


if(sum(gc2[,'Interval'] != targets[,'Interval']) != 0){
	stop("Order of targets do not match\n");
}
gc2 <- gc2[,-c(1,2),drop=F];

GC<-as.numeric(targets[,grep("GC_150",colnames(targets))]);


# New implementation - use optimize to search for function minimum - DC June 11th 2013
index <- which(targets[,'Interval'] %in% tiling.probes);
span.fits <- do.call('rbind',list(apply(gc2,2,function(column){
	column_sqrt<-sqrt(column[index]);
	gc.bias <- GC[index];

	testspan <- function(spanvalue){
		temp<-loess(column_sqrt~gc.bias,span=spanvalue);
		temp2<-predict(temp) #Calculation of the loess fit for each spanvalue
		normalized<-column_sqrt-temp2+median(column_sqrt) #Data normalized for each spanvalue

		fit<-loess(normalized~gc.bias);
		fit2<-predict(fit) #The "fit" of each normalized data point - the result gives the flat-ish line
		spanvar=var(fit2,na.rm=TRUE) #Calculate the variance to find the flattest line after fitting
		return(round(spanvar,5));
	}
	optimize.obj <-	optimize(testspan,interval=c(0.3,0.75),maximum=F);
	return(c('min'=optimize.obj$minimum,'obj'=optimize.obj$objective));
})));
span.fits <- t(span.fits);

out_file= paste(prefix,"_",type,"_loessnorm.pdf", sep="")
pdf(out_file, height=8.5, width=11)
plot(0:10, type = "n", xaxt="n", yaxt="n", bty="n", xlab = "", ylab = "")
text(11, 10, "Memorial Sloan Kettering",adj=1)
text(11, 9.5, "Berger Lab",adj=1)
text(11, 9, date(),adj=1)
text(1, 8, "Loess Normalization results",adj=0,cex=1.5,font=2)

targets.inclY <- tar.sort;
gc2.inclY <- d.sort[match(targets.inclY[,'Interval'],d.sort[,'Interval']),];
gc2.inclY <- gc2.inclY[,-c(1,2),drop=F];

index <- which(targets[,'Interval'] %in% tiling.probes);
index.inclY <- which(targets.inclY[,'Interval'] %in% tiling.probes);

GC.inclY <-as.numeric(targets.inclY[,grep("GC_150",colnames(targets.inclY))]);

norm_rt <- do.call('cbind',lapply(seq(1,ncol(gc2),1),function(i){
	column_sqrt<-sqrt(gc2.inclY[-index.inclY,i]);
	gc.bias <- GC.inclY[-index.inclY];
	loess.obj <-loess(column_sqrt~gc.bias,span=span.fits[i,'min']);
	temp2<-predict(loess.obj);
	normalized.filt<-(column_sqrt-temp2+median(column_sqrt))/(median(column_sqrt[which(column_sqrt != 0)]));

	column_sqrt.tiling <- sqrt(gc2[index,i]); # exclude Y
	gc.tiling <- GC[index]; 				  # exclude Y

	column_sqrt.tiling.inclY <- sqrt(gc2.inclY[index.inclY,i]); # exclude Y
	gc.tiling.inclY <- GC.inclY[index.inclY];

	#loess.obj.tiling <-loess(column_sqrt.tiling~gc.tiling,span=span.fits[i,'min']); # Learn model excluding Y, but apply on newdata which has Y.
	#temp2.tiling<-predict(loess.obj.tiling,newdata=gc.tiling.inclY);

	loess.obj.tiling <-loess(column_sqrt.tiling.inclY~gc.tiling.inclY,span=span.fits[i,'min']);
	temp2.tiling<-predict(loess.obj.tiling)
	#normalized.tiling<-(column_sqrt.tiling.inclY-temp2.tiling+median(column_sqrt))/(median(column_sqrt[which(column_sqrt != 0)]));
	normalized.tiling<-(column_sqrt.tiling.inclY-temp2.tiling+median(column_sqrt.tiling.inclY))/(median(column_sqrt.tiling.inclY[which(column_sqrt.tiling.inclY != 0)]));
	temp2.all <- GC.inclY;
	temp2.all[which(targets.inclY[,'Interval'] %in% tiling.probes)] <- temp2.tiling;
	temp2.all[which(!(targets.inclY[,'Interval'] %in% tiling.probes))] <- temp2;

	normalized <-GC.inclY;
	normalized[which(targets.inclY[,'Interval'] %in% tiling.probes)] <- normalized.tiling;
	normalized[which(!(targets.inclY[,'Interval'] %in% tiling.probes))] <- normalized.filt;

	## Debug: Plot
	column_sqrt.all <- sqrt(gc2.inclY[,i]);
	par(mfrow=c(2,2))
	plot(GC.inclY[-index.inclY],column_sqrt.all[-index.inclY],ylim=c(0,60),main=paste("SqRt_",colnames(gc2)[i],sep=""),col='black',xlim=c(0.2,0.9),xlab='pGC',ylab='sqrt_cov', cex=0.75);
	par(new=T);
	plot(GC.inclY[index.inclY],column_sqrt.all[index.inclY],ylim=c(0,60),col='red',xlim=c(0.2,0.9),xlab='',ylab='', cex=0.75);
	legend(x='topright',col=c('black','red'),legend=c('Panel_A','Panel_B'),pch=1);
	par(new=F);

	plot(GC.inclY,temp2.all,ylim=c(0,60),main=paste("Loess fit. Span:",span.fits[i,'min'],sep=""));
	##Normalize the data for the purpose of the graph.

        #normalized<-column_sqrt.all-temp2.all+median(column_sqrt);

	#plot(GC.inclY,normalized,ylim=c(0,2),main="Normalized")
	plot(GC.inclY[index.inclY],normalized[index.inclY],ylim=c(0,2),main="Normalized", col="red", xlab="GC.inclY",xlim=c(0.2,0.9), cex=0.75 )
	par(new=T)
	plot(GC.inclY[-index.inclY],normalized[-index.inclY],ylim=c(0,2),main="Normalized", col="black", xlab='',ylab='',xlim=c(0.2,0.9), cex=0.75)
	par(new=F)
	fit<-loess(normalized~GC.inclY);
	fit2<-predict(fit,newdata=GC.inclY);
	plot(GC.inclY,fit2,ylim=c(0,2),main="Normalized fit")
	return(normalized);
}));
dev.off();

norm=(norm_rt^2);
colnames(norm)<-colnames(gc2.inclY);
normtable=data.frame('Order'=targets.inclY[,"Order"],'Interval'=targets.inclY[,"Interval"],'genes'=as.character(targets.inclY[,"Gene"]),norm);

write.table(normtable,outtablename,sep="\t",row.names=FALSE,col.names=TRUE)
