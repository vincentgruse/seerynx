import { useState } from "react";
import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { Star, Trash2, Check, ClipboardList, Bird } from "lucide-react";
import { StatCard } from "@/components/StatCard";
import { Skeleton } from "@/components/ui/skeleton";
import { Card, CardContent } from "@/components/ui/card";
import { CollapsibleSection } from "@/components/CollapsibleSection";
import { Button } from "@/components/ui/button";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { useQuery } from "@tanstack/react-query";
import { getLifeListApiSightingsFirstGetOptions } from "@/client/@tanstack/react-query.gen";
import { useDeleteSpecies } from "@/features/sightings/hooks/useSightings";
import { formatTimestamp } from "@/utils/format";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/life-list")({
  component: LifeList,
});

function LifeList() {
  const { data: lifeList, isLoading } = useQuery(
    getLifeListApiSightingsFirstGetOptions(),
  );
  const deleteSpecies = useDeleteSpecies();
  const navigate = useNavigate();

  const [selectMode, setSelectMode] = useState(false);
  const [selected, setSelected] = useState<string[]>([]);
  const [confirmOpen, setConfirmOpen] = useState(false);

  const toggleSelectMode = () => {
    setSelectMode((prev) => !prev);
    setSelected([]);
  };

  const toggleSelected = (commonName: string) => {
    setSelected((prev) =>
      prev.includes(commonName)
        ? prev.filter((n) => n !== commonName)
        : [...prev, commonName],
    );
  };

  const handleConfirmDelete = () => {
    deleteSpecies.mutate(
      { body: { common_names: selected } },
      {
        onSuccess: () => {
          setSelected([]);
          setSelectMode(false);
          setConfirmOpen(false);
        },
      },
    );
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Life List</h1>
        <p className="text-muted-foreground text-sm mt-1">
          Every species you've ever recorded
        </p>
      </div>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard
          title="Total Species"
          value={lifeList?.length ?? 0}
          icon={Star}
          subtitle="lifetime sightings"
        />
      </div>
      <CollapsibleSection
        title="All Species"
        maxHeight="max-h-[65vh]"
        headerClassName="pb-4"
        actions={
          lifeList &&
          lifeList.length > 0 && (
            <div className="flex items-center gap-2">
              {selectMode && (
                <Button
                  variant="destructive"
                  size="sm"
                  disabled={selected.length === 0 || deleteSpecies.isPending}
                  onClick={() => setConfirmOpen(true)}
                >
                  <Trash2 />
                  Delete Selected{" "}
                  {selected.length > 0 && `(${selected.length})`}
                </Button>
              )}
              <Button variant="outline" size="sm" onClick={toggleSelectMode}>
                {selectMode ? "Cancel" : "Select species"}
              </Button>
            </div>
          )
        }
      >
        {isLoading ? (
          <div className="space-y-2">
            {Array.from({ length: 10 }).map((_, i) => (
              <Skeleton key={i} className="h-16 rounded-lg" />
            ))}
          </div>
        ) : lifeList?.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 text-muted-foreground">
            <ClipboardList className="size-12 mb-4" />
            <p className="text-sm">No species recorded yet</p>
            <p className="text-xs mt-1">
              Check back after your first sighting!
            </p>
          </div>
        ) : (
          <div className="space-y-2">
            {lifeList?.map((entry, i) => (
              <Card
                key={entry.common_name}
                className={cn(
                  "cursor-pointer",
                  !selectMode &&
                    "hover:shadow-md hover:scale-[1.01] transition duration-300 ease-out",
                  selectMode &&
                    selected.includes(entry.common_name) &&
                    "ring-2 ring-primary",
                )}
                onClick={
                  selectMode
                    ? () => toggleSelected(entry.common_name)
                    : () =>
                        navigate({
                          to: "/species/$name",
                          params: { name: entry.common_name },
                        })
                }
              >
                <CardContent className="flex items-center justify-between py-2 px-4">
                  <div className="flex items-center gap-4">
                    {selectMode ? (
                      <div
                        className={cn(
                          "flex size-6 items-center justify-center rounded-full border-2",
                          selected.includes(entry.common_name)
                            ? "border-primary bg-primary text-primary-foreground"
                            : "border-muted-foreground/50",
                        )}
                      >
                        {selected.includes(entry.common_name) && (
                          <Check className="size-4" />
                        )}
                      </div>
                    ) : (
                      <span className="text-muted-foreground text-base font-mono w-6">
                        {i + 1}
                      </span>
                    )}
                    {entry.species_photo_path ? (
                      <img
                        src={`${import.meta.env.VITE_API_URL}/api/photos/${entry.species_photo_path}`}
                        alt={entry.common_name}
                        className="w-24 h-auto rounded-lg"
                      />
                    ) : (
                      <div className="size-24 rounded-lg bg-muted flex items-center justify-center">
                        <Bird className="size-8 text-muted-foreground" />
                      </div>
                    )}
                    <div>
                      <p className="font-semibold text-sm">
                        {entry.common_name}
                      </p>
                      {entry.scientific_name && (
                        <p className="text-xs text-muted-foreground italic">
                          {entry.scientific_name}
                        </p>
                      )}
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-xs text-muted-foreground">First seen</p>
                    <p className="text-xs font-medium">
                      {formatTimestamp(entry.first_seen)}
                    </p>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </CollapsibleSection>

      <AlertDialog open={confirmOpen} onOpenChange={setConfirmOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>
              Delete {selected.length} species?
            </AlertDialogTitle>
            <AlertDialogDescription>
              This will permanently delete every sighting and audio detection
              recorded for{" "}
              {selected.length === 1 ? "this species" : "these species"} (
              {selected.join(", ")}), including their photos. This cannot be
              undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              variant="destructive"
              disabled={deleteSpecies.isPending}
              onClick={handleConfirmDelete}
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
