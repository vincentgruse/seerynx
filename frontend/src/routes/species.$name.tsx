import { createFileRoute, Link } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { ArrowLeft, Bird } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Dialog, DialogContent, DialogTrigger } from "@/components/ui/dialog";
import { getSpeciesApiSpeciesCommonNameGetOptions } from "@/client/@tanstack/react-query.gen";

export const Route = createFileRoute("/species/$name")({
  component: SpeciesSpotlight,
});

const SECTIONS: {
  key: "habitat" | "food" | "nesting" | "behavior" | "conservation";
  title: string;
}[] = [
  { key: "habitat", title: "Habitat" },
  { key: "food", title: "Food" },
  { key: "nesting", title: "Nesting" },
  { key: "behavior", title: "Behavior" },
  { key: "conservation", title: "Conservation" },
];

function stripLeadingTitle(value: string, title: string): string {
  if (value.startsWith(title)) {
    return value.slice(title.length).trimStart();
  }
  return value;
}

function SpeciesSpotlight() {
  const { name } = Route.useParams();
  const commonName = decodeURIComponent(name);

  const { data: species, isLoading } = useQuery(
    getSpeciesApiSpeciesCommonNameGetOptions({
      path: { common_name: commonName },
    }),
  );

  return (
    <div className="space-y-6">
      <Link
        to="/nearby"
        className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground"
      >
        <ArrowLeft className="size-4" />
        Back
      </Link>

      {isLoading ? (
        <div className="space-y-4">
          <Skeleton className="h-[30vh] w-full rounded-xl" />
          <Skeleton className="h-8 w-64" />
          <Skeleton className="h-32 w-full" />
        </div>
      ) : !species ? (
        <div className="flex flex-col items-center justify-center py-16 text-muted-foreground">
          <Bird className="size-12 mb-4" />
          <p className="text-sm">No information found for {commonName}</p>
        </div>
      ) : (
        <Card className="pt-0 overflow-hidden">
          {species.photo_path ? (
            <Dialog>
              <DialogTrigger className="block h-[30vh] w-full bg-muted relative overflow-hidden rounded-t-xl cursor-zoom-in">
                <img
                  src={`${import.meta.env.VITE_API_URL}/api/photos/${species.photo_path}`}
                  alt={species.common_name}
                  className="w-full h-full object-contain rounded-t-xl"
                />
              </DialogTrigger>
              <DialogContent className="max-w-[90vw] max-h-[90vh]">
                <img
                  src={`${import.meta.env.VITE_API_URL}/api/photos/${species.photo_path}`}
                  alt={species.common_name}
                  className="max-w-[90vw] max-h-[90vh] rounded-xl object-contain"
                />
              </DialogContent>
            </Dialog>
          ) : (
            <div className="h-[30vh] w-full bg-muted flex items-center justify-center rounded-t-xl">
              <Bird className="size-16 text-muted-foreground" />
            </div>
          )}
          <CardHeader>
            <CardTitle className="text-2xl">{species.common_name}</CardTitle>
            {species.scientific_name && (
              <p className="text-sm text-muted-foreground italic">
                {species.scientific_name}
              </p>
            )}
          </CardHeader>
          <CardContent className="space-y-6">
            {SECTIONS.map(({ key, title }) => {
              const value = species[key];
              if (!value) return null;
              return (
                <div key={key}>
                  <h3 className="font-semibold text-sm mb-1">{title}</h3>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    {stripLeadingTitle(value, title)}
                  </p>
                </div>
              );
            })}
            {!SECTIONS.some(({ key }) => species[key]) && (
              <p className="text-sm text-muted-foreground">
                No additional information available for this species yet.
              </p>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
