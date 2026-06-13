import { useState } from "react";
import { ChevronDown } from "lucide-react";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface CollapsibleSectionProps {
  title: string;
  defaultOpen?: boolean;
  actions?: React.ReactNode;
  /** Tailwind max-height class applied to the content when expanded, enabling it to scroll in place. */
  maxHeight?: string;
  /** Additional classes applied to the header row, e.g. to add margin below it. */
  headerClassName?: string;
  /** Compact content shown when the section is collapsed, e.g. a mini chart. */
  collapsedPreview?: React.ReactNode;
  children: React.ReactNode;
}

export function CollapsibleSection({
  title,
  defaultOpen = true,
  actions,
  maxHeight,
  headerClassName,
  collapsedPreview,
  children,
}: CollapsibleSectionProps) {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <Card>
      <Collapsible open={open} onOpenChange={setOpen}>
        <CardHeader
          className={cn(
            "flex flex-row items-center justify-between gap-2",
            headerClassName,
          )}
        >
          <CollapsibleTrigger className="flex items-center gap-2 text-left">
            <ChevronDown
              className={cn(
                "h-4 w-4 text-muted-foreground transition-transform",
                !open && "-rotate-90",
              )}
            />
            <CardTitle>{title}</CardTitle>
          </CollapsibleTrigger>
          {actions}
        </CardHeader>
        {!open && collapsedPreview && (
          <CardContent className="pt-0">{collapsedPreview}</CardContent>
        )}
        <CollapsibleContent>
          <CardContent
            className={cn(
              "pt-0",
              maxHeight && cn("overflow-y-auto", maxHeight),
            )}
          >
            {maxHeight ? <div className="p-1">{children}</div> : children}
          </CardContent>
        </CollapsibleContent>
      </Collapsible>
    </Card>
  );
}
