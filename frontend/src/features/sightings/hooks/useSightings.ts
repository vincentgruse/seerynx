import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  getSightingsApiSightingsGetOptions,
  getTodayFeederApiSightingsTodayGetOptions,
  getStreakApiSightingsStreakGetOptions,
  getHeatmapApiSightingsHeatmapGetOptions,
  deleteSightingsApiSightingsDeleteMutation,
  deleteSpeciesApiSightingsSpeciesDeleteMutation,
} from "@/client/@tanstack/react-query.gen";

export function useTodaySightings() {
  return useQuery(getTodayFeederApiSightingsTodayGetOptions());
}

export function useLatestSightings(limit = 10) {
  return useQuery({
    ...getSightingsApiSightingsGetOptions({ query: { limit } }),
    refetchInterval: 20000,
  });
}

export function useStreak() {
  return useQuery(getStreakApiSightingsStreakGetOptions());
}

export function useHeatmap() {
  return useQuery(getHeatmapApiSightingsHeatmapGetOptions());
}

export function useDeleteSightings() {
  const queryClient = useQueryClient();

  return useMutation({
    ...deleteSightingsApiSightingsDeleteMutation(),
    onSuccess: () => {
      queryClient.invalidateQueries({
        predicate: (query) => {
          const id = (query.queryKey[0] as { _id?: string } | undefined)?._id;
          return id?.toLowerCase().includes("sighting") ?? false;
        },
      });
    },
  });
}

export function useDeleteSpecies() {
  const queryClient = useQueryClient();

  return useMutation({
    ...deleteSpeciesApiSightingsSpeciesDeleteMutation(),
    onSuccess: () => {
      queryClient.invalidateQueries({
        predicate: (query) => {
          const id = (query.queryKey[0] as { _id?: string } | undefined)?._id;
          return id?.toLowerCase().includes("sighting") ?? false;
        },
      });
    },
  });
}
