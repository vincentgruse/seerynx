import { useState } from "react";
import { Trash2, type LucideIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { CollapsibleSection } from "@/components/CollapsibleSection";
import { SightingCard } from "@/features/sightings/components/SightingCard";
import { useDeleteSightings } from "@/features/sightings/hooks/useSightings";
import type { SightingResponse } from "@/client/types.gen";

interface SightingsGridProps {
  title: string;
  sightings: SightingResponse[] | undefined;
  isLoading: boolean;
  emptyIcon: LucideIcon;
  emptyMessage: string;
  emptySubMessage?: string;
  showDetectionCount?: boolean;
}

function groupBySpecies(sightings: SightingResponse[]): SightingResponse[][] {
  const groups = new Map<string, SightingResponse[]>();
  for (const sighting of sightings) {
    const existing = groups.get(sighting.common_name);
    if (existing) {
      existing.push(sighting);
    } else {
      groups.set(sighting.common_name, [sighting]);
    }
  }
  return Array.from(groups.values());
}

export function SightingsGrid({
  title,
  sightings,
  isLoading,
  emptyIcon: EmptyIcon,
  emptyMessage,
  emptySubMessage,
  showDetectionCount = true,
}: SightingsGridProps) {
  const [selectMode, setSelectMode] = useState(false);
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const deleteSightings = useDeleteSightings();

  const groups = sightings ? groupBySpecies(sightings) : undefined;

  const toggleSelectMode = () => {
    setSelectMode((prev) => !prev);
    setSelectedIds([]);
  };

  const toggleSelectedGroup = (ids: number[]) => {
    setSelectedIds((prev) => {
      const allSelected = ids.every((id) => prev.includes(id));
      return allSelected
        ? prev.filter((id) => !ids.includes(id))
        : [...prev, ...ids.filter((id) => !prev.includes(id))];
    });
  };

  const handleDeleteSelected = () => {
    if (selectedIds.length === 0) return;
    deleteSightings.mutate(
      { body: { ids: selectedIds } },
      {
        onSuccess: () => {
          setSelectedIds([]);
          setSelectMode(false);
        },
      },
    );
  };

  const handleDeleteGroup = (ids: number[]) => {
    deleteSightings.mutate({ body: { ids } });
  };

  return (
    <CollapsibleSection
      title={title}
      maxHeight="max-h-[65vh]"
      actions={
        sightings &&
        sightings.length > 0 && (
          <div className="flex items-center gap-2">
            {selectMode && (
              <Button
                variant="destructive"
                size="sm"
                disabled={selectedIds.length === 0 || deleteSightings.isPending}
                onClick={handleDeleteSelected}
              >
                <Trash2 />
                Delete Selected{" "}
                {selectedIds.length > 0 && `(${selectedIds.length})`}
              </Button>
            )}
            <Button variant="outline" size="sm" onClick={toggleSelectMode}>
              {selectMode ? "Cancel" : "Select birds"}
            </Button>
          </div>
        )
      }
    >
      {isLoading ? (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {Array.from({ length: 8 }).map((_, i) => (
            <Skeleton key={i} className="aspect-video rounded-lg" />
          ))}
        </div>
      ) : sightings?.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-16 text-muted-foreground">
          <EmptyIcon className="size-12 mb-4" />
          <p className="text-sm">{emptyMessage}</p>
          {emptySubMessage && <p className="text-xs mt-1">{emptySubMessage}</p>}
        </div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {groups?.map((group) => {
            const ids = group.map((s) => s.id);
            return (
              <SightingCard
                key={group[0].id}
                sightings={group}
                selectMode={selectMode}
                selected={ids.every((id) => selectedIds.includes(id))}
                onToggleSelect={() => toggleSelectedGroup(ids)}
                onDelete={() => handleDeleteGroup(ids)}
                showDetectionCount={showDetectionCount}
              />
            );
          })}
        </div>
      )}
    </CollapsibleSection>
  );
}
