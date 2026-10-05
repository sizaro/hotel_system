import {createContext,useCallback,useContext,useEffect,useMemo,useState} from 'react';
import {api} from '../services/api';
import {cacheOffline,readOffline} from '../services/offline';

const fallback={name:'Hotel Management Platform',short_name:'Hotel',tagline:'Stay well. Meet beautifully. Return often.',description:'A welcoming destination for restful stays, memorable dining and thoughtfully hosted events.',currency:'UGX',timezone:'Africa/Kampala',city:'Kampala',country:'Uganda',phone:'',email:'',address:'',logo_url:'',hero_image_url:'https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=1800&q=85',social_links:{},services:[]};
const HotelContext=createContext({hotel:fallback,loading:true,refreshHotel:async()=>{}});
export function HotelProvider({children}){
  const[hotel,setHotel]=useState(fallback);const[loading,setLoading]=useState(true);
  const refreshHotel=useCallback(async()=>{const{data}=await api.get('/hotel/settings/');setHotel({...fallback,...data});await cacheOffline('hotel-settings',data);return data},[]);
  useEffect(()=>{let active=true;(async()=>{try{const data=await refreshHotel();if(!active)return data}catch{const saved=await readOffline('hotel-settings');if(active&&saved)setHotel({...fallback,...saved})}finally{if(active)setLoading(false)}})();return()=>{active=false}},[refreshHotel]);
  const value=useMemo(()=>({hotel,loading,refreshHotel,money:value=>new Intl.NumberFormat('en-UG',{style:'currency',currency:hotel.currency||'UGX',maximumFractionDigits:0}).format(Number(value||0))}),[hotel,loading,refreshHotel]);
  return <HotelContext.Provider value={value}>{children}</HotelContext.Provider>
}
export const useHotel=()=>useContext(HotelContext);
