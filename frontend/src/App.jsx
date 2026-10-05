import {lazy,Suspense} from 'react';
import {Navigate,Route,Routes} from 'react-router-dom';
import PublicLayout from './layouts/PublicLayout';
import AdminLayout from './layouts/AdminLayout';
import ProtectedRoute from './routes/ProtectedRoute';
import RoleRoute from './routes/RoleRoute';
const Home=lazy(()=>import('./pages/public/Home')); const About=lazy(()=>import('./pages/public/About')); const Rooms=lazy(()=>import('./pages/public/Rooms')); const Services=lazy(()=>import('./pages/public/Services')); const Events=lazy(()=>import('./pages/public/Events')); const Contact=lazy(()=>import('./pages/public/Contact')); const Booking=lazy(()=>import('./pages/public/Booking')); const Login=lazy(()=>import('./pages/public/Login')); const Register=lazy(()=>import('./pages/public/Register')); const Dashboard=lazy(()=>import('./pages/dashboard'));
const CommandCenter=lazy(()=>import('./pages/dashboard/CommandCenter'));const Reservations=lazy(()=>import('./pages/dashboard/Reservations'));const Finance=lazy(()=>import('./pages/dashboard/Finance'));const PointOfSale=lazy(()=>import('./pages/dashboard/PointOfSale'));const Inventory=lazy(()=>import('./pages/dashboard/Inventory'));const EventsManagement=lazy(()=>import('./pages/dashboard/EventsManagement'));const DailyOperations=lazy(()=>import('./pages/dashboard/DailyOperations'));const Marketing=lazy(()=>import('./pages/dashboard/Marketing'));const Reports=lazy(()=>import('./pages/dashboard/Reports'));const Assistant=lazy(()=>import('./pages/dashboard/Assistant'));
const Settings=lazy(()=>import('./pages/dashboard/Settings'));

function Loading(){return <div className="grid min-h-[50vh] place-items-center bg-cream"><span className="h-10 w-10 animate-spin rounded-full border-4 border-forest border-t-gold"/></div>}
export default function App(){return <Suspense fallback={<Loading/>}><Routes>
  <Route element={<PublicLayout/>}>
    <Route index element={<Home/>}/><Route path="about" element={<About/>}/><Route path="rooms" element={<Rooms/>}/>
    <Route path="services" element={<Services/>}/><Route path="events" element={<Events/>}/><Route path="contact" element={<Contact/>}/>
    <Route path="book" element={<Booking/>}/><Route path="login" element={<Login/>}/><Route path="register" element={<Register/>}/>
  </Route>
  <Route element={<ProtectedRoute/>}><Route path="dashboard" element={<AdminLayout/>}><Route index element={<Dashboard/>}/><Route path="command-center" element={<RoleRoute roles={['MANAGER','ADMIN','OWNER']}><CommandCenter/></RoleRoute>}/><Route path="reservations" element={<RoleRoute roles={['RECEPTIONIST','MANAGER','ADMIN','OWNER']}><Reservations/></RoleRoute>}/><Route path="finance" element={<RoleRoute roles={['FINANCE','RECEPTIONIST','MANAGER','ADMIN','OWNER']}><Finance/></RoleRoute>}/><Route path="pos" element={<RoleRoute roles={['BAR','RESTAURANT','FINANCE','MANAGER','ADMIN','OWNER']}><PointOfSale/></RoleRoute>}/><Route path="inventory" element={<RoleRoute roles={['BAR','RESTAURANT','MANAGER','ADMIN','OWNER']}><Inventory/></RoleRoute>}/><Route path="events" element={<RoleRoute roles={['EVENTS','RECEPTIONIST','MANAGER','ADMIN','OWNER']}><EventsManagement/></RoleRoute>}/><Route path="operations" element={<RoleRoute roles={['HOUSEKEEPING','EMPLOYEE','MANAGER','ADMIN','OWNER']}><DailyOperations/></RoleRoute>}/><Route path="marketing" element={<RoleRoute roles={['MARKETING','MANAGER','ADMIN','OWNER']}><Marketing/></RoleRoute>}/><Route path="reports" element={<RoleRoute roles={['FINANCE','MANAGER','ADMIN','OWNER']}><Reports/></RoleRoute>}/><Route path="assistant" element={<Assistant/>}/><Route path="settings" element={<Settings/>}/></Route></Route>
  <Route path="*" element={<Navigate to="/" replace/>}/>
</Routes></Suspense>}
