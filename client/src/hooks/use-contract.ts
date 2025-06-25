import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

export function useContract(contractId: number) {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  const contractQuery = useQuery({
    queryKey: ['/api/contracts', contractId],
    queryFn: () => api.getContract(contractId),
    enabled: !!contractId,
  });

  const updateContractMutation = useMutation({
    mutationFn: (updates: any) => api.updateContract(contractId, updates),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['/api/contracts', contractId] });
      toast({
        title: "Contract updated",
        description: "Your changes have been saved successfully.",
      });
    },
    onError: () => {
      toast({
        title: "Error",
        description: "Failed to update contract. Please try again.",
        variant: "destructive",
      });
    },
  });

  const commentsQuery = useQuery({
    queryKey: ['/api/contracts', contractId, 'comments'],
    queryFn: () => api.getContractComments(contractId),
    enabled: !!contractId,
  });

  const suggestionsQuery = useQuery({
    queryKey: ['/api/contracts', contractId, 'suggestions'],
    queryFn: () => api.getContractSuggestions(contractId),
    enabled: !!contractId,
  });

  const versionsQuery = useQuery({
    queryKey: ['/api/contracts', contractId, 'versions'],
    queryFn: () => api.getContractVersions(contractId),
    enabled: !!contractId,
  });

  return {
    contract: contractQuery.data,
    isLoading: contractQuery.isLoading,
    updateContract: updateContractMutation.mutate,
    isUpdating: updateContractMutation.isPending,
    comments: commentsQuery.data || [],
    suggestions: suggestionsQuery.data || [],
    versions: versionsQuery.data || [],
    refetchComments: commentsQuery.refetch,
    refetchSuggestions: suggestionsQuery.refetch,
    refetchVersions: versionsQuery.refetch,
  };
}
