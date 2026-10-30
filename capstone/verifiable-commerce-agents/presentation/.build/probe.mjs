import {FileBlob,PresentationFile} from '@oai/artifact-tool';
const p=await PresentationFile.importPptx(await FileBlob.load('/Volumes/DOCK1TBFILES/AI/AI Agents/capstone/verifiable-commerce-agents/presentation/output/Tau2_Bench_Overview_EN.pptx'));
console.log(p.help('*',{search:'remove',include:['index','notes'],maxChars:4000}));
