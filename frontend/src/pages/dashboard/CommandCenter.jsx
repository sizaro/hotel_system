import {useEffect,useState} from 'react';
import {Banknote,CalendarCheck,DoorOpen,RefreshCw,TriangleAlert} from 'lucide-react';
import {hotelOps} from '../../services/hotelOperationsService';
import {PageTitle,Panel} from '../../components/dashboard/Panel';
import {useHotel} from '../../context/HotelContext';

export default function CommandCenter(){
  const[data,setData]=useState(null);const[loading,setLoading]=useState(true);const{money}=useHotel();
  const load=()=>{setLoading(true);hotelOps.commandCenter().then(setData).finally(()=>setLoading(false))};
  useEffect(()=>{hotelOps.commandCenter().then(setData).finally(()=>setLoading(false))},[]);
  if(loading)return <div className="py-20 text-center">Loading live hotel position…</div>;
  const cards=[[DoorOpen,'Available rooms',data?.rooms.available],[CalendarCheck,'Active stays',data?.stays.active],[Banknote,'Payments today',money(data?.finance.payments_today)],[TriangleAlert,'Open maintenance',data?.operations.maintenance_open]];
  return <><PageTitle eyebrow="Business command center" title="The hotel, at a glance." copy="Every figure comes from authoritative operational records."/><div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-4">{cards.map(([Icon,label,value])=><div className="surface-card p-6" key={label}><Icon className="text-gold"/><p className="mt-5 text-3xl font-black">{value}</p><p className="text-sm text-slate-500">{label}</p></div>)}</div><div className="mt-7 grid gap-6 lg:grid-cols-2"><Panel title="Today’s movement"><dl className="grid grid-cols-2 gap-5 text-sm"><Metric label="Arrivals" value={data?.stays.arrivals_today}/><Metric label="Departures" value={data?.stays.departures_today}/><Metric label="Booking requests" value={data?.stays.booking_requests}/><Metric label="Upcoming events" value={data?.events.upcoming}/></dl></Panel><Panel title="Needs attention" action={<button onClick={load}><RefreshCw size={18}/></button>}><dl className="grid grid-cols-2 gap-5 text-sm"><Metric label="Housekeeping open" value={data?.operations.housekeeping_open}/><Metric label="Maintenance open" value={data?.operations.maintenance_open}/><Metric label="Sync conflicts" value={data?.operations.sync_conflicts}/><Metric label="Open folios" value={data?.finance.open_folios}/></dl></Panel></div></>
}
function Metric({label,value}){return <div className="rounded-xl bg-cream p-4"><dt className="text-slate-500">{label}</dt><dd className="mt-1 text-2xl font-black">{value}</dd></div>}
