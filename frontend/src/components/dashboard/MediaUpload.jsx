import {Camera,UploadCloud} from 'lucide-react';
import {useRef,useState} from 'react';
import {toast} from 'sonner';
import {api} from '../../services/api';

export default function MediaUpload({label,value,onChange,accept='image/*'}){
  const fileRef=useRef(null);const cameraRef=useRef(null);const[busy,setBusy]=useState(false);
  const upload=async file=>{if(!file)return;setBusy(true);try{const body=new FormData();body.append('file',file);const{data}=await api.post('/hotel/media/upload/',body,{headers:{'Content-Type':'multipart/form-data'}});onChange(data.url);toast.success(`${label} uploaded.`)}catch(error){toast.error(error.response?.data?.detail||'File could not be uploaded.')}finally{setBusy(false)}};
  return <div className="md:col-span-2"><p className="text-sm font-bold">{label}</p>{value&&<img src={value} alt="Current upload" className="mt-2 h-28 w-full rounded-2xl object-cover"/>}<div className="mt-2 flex flex-wrap gap-2"><button type="button" className="btn-secondary !px-3 !py-2" disabled={busy} onClick={()=>fileRef.current?.click()}><UploadCloud size={16}/>{busy?'Uploading…':'Choose file'}</button><button type="button" className="btn-secondary !px-3 !py-2" disabled={busy} onClick={()=>cameraRef.current?.click()}><Camera size={16}/>Take photo</button></div><input ref={fileRef} hidden type="file" accept={accept} onChange={e=>upload(e.target.files?.[0])}/><input ref={cameraRef} hidden type="file" accept="image/*" capture="environment" onChange={e=>upload(e.target.files?.[0])}/></div>
}
