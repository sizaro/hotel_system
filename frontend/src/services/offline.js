import {openDB} from 'idb';
const database=openDB('hotel-platform',1,{upgrade(db){if(!db.objectStoreNames.contains('operations'))db.createObjectStore('operations',{keyPath:'id'});if(!db.objectStoreNames.contains('cache'))db.createObjectStore('cache')}});
export async function queueOperation(type,payload){const db=await database;const operation={id:crypto.randomUUID(),type,payload,status:'PENDING',createdAt:new Date().toISOString()};await db.put('operations',operation);window.dispatchEvent(new Event('hotel-sync-change'));return operation}
export async function pendingOperations(){return (await database).getAll('operations')}
export async function updateOperation(operation){return (await database).put('operations',operation)}
export async function removeOperation(id){return (await database).delete('operations',id)}
export async function flushOperations(send){const operations=await pendingOperations();const outcomes=[];for(const operation of operations){try{await updateOperation({...operation,status:'SYNCHRONIZING'});const result=await send(operation);await removeOperation(operation.id);outcomes.push({id:operation.id,status:'SYNCED',result})}catch(error){const conflict=error.response?.status===409;await updateOperation({...operation,status:conflict?'CONFLICT':'FAILED',error:error.response?.data||error.message});outcomes.push({id:operation.id,status:conflict?'CONFLICT':'FAILED'})}}localStorage.setItem('hotel_last_sync',new Date().toISOString());window.dispatchEvent(new Event('hotel-sync-change'));return outcomes}
export async function cacheOffline(key,value){return (await database).put('cache',value,key)}
export async function readOffline(key){return (await database).get('cache',key)}
