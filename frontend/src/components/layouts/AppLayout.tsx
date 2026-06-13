import { Link, useRouterState } from "@tanstack/react-router";
import {
  Activity,
  CalendarDays,
  Home,
  LineChart,
  List,
  Mic2,
  ThermometerSun,
} from "lucide-react";
import wordmarkLight from "@/assets/seerynx-light.svg";
import wordmarkDark from "@/assets/seerynx-dark.svg";
import { ThemeToggle } from "../ThemeToggle";
import { NotificationBell } from "../NotificationBell";
import { FeederStatusIndicator } from "../FeederStatusIndicator";
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarInset,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar";

const navItems = [
  { label: "Dashboard", icon: Home, to: "/" },
  { label: "Nearby Birds", icon: Mic2, to: "/nearby" },
  { label: "Life List", icon: List, to: "/life-list" },
  { label: "Calendar", icon: CalendarDays, to: "/calendar" },
  { label: "Weather", icon: ThermometerSun, to: "/weather" },
  { label: "Weekly Summary", icon: Activity, to: "/summary" },
  { label: "Insights", icon: LineChart, to: "/insights" },
];

export function AppLayout({ children }: { children: React.ReactNode }) {
  const router = useRouterState();
  const currentPath = router.location.pathname;

  return (
    <SidebarProvider className="min-h-screen w-full">
      <Sidebar collapsible="icon">
        <SidebarHeader className="p-0 mt-4 ms-4 items-start">
          <img
            src={wordmarkLight}
            alt="Seerynx"
            className="h-12 w-auto truncate group-data-[state=collapsed]/sidebar:hidden dark:hidden"
          />
          <img
            src={wordmarkDark}
            alt="Seerynx"
            className="hidden h-12 w-auto truncate group-data-[state=collapsed]/sidebar:hidden dark:block"
          />
        </SidebarHeader>
        <SidebarContent>
          <SidebarGroup>
            <SidebarGroupLabel>Navigation</SidebarGroupLabel>
            <SidebarGroupContent>
              <SidebarMenu>
                {navItems.map((item) => (
                  <SidebarMenuItem key={item.to}>
                    <SidebarMenuButton
                      isActive={currentPath === item.to}
                      render={<Link to={item.to} />}
                    >
                      <item.icon className="h-4 w-4" />
                      <span>{item.label}</span>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                ))}
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>
        </SidebarContent>
      </Sidebar>
      <SidebarInset>
        <header className="flex items-center justify-between h-14 border-b px-4 bg-background/80 backdrop-blur-sm sticky top-0 z-10">
          <SidebarTrigger />
          <div className="flex items-center gap-2">
            <FeederStatusIndicator />
            <NotificationBell />
            <ThemeToggle />
          </div>
        </header>
        <main className="flex-1 p-6 overflow-auto">{children}</main>
      </SidebarInset>
    </SidebarProvider>
  );
}
