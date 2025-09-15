'use client';
import useSWR from 'swr';
export function usePolling<T>(key: string, fetcher: ()=>Promise<T>, ms=5000){
  const { data, error, isLoading, mutate } = useSWR(key, fetcher, { refreshInterval: ms });
  return { data, error, isLoading, refresh: ()=>mutate() };
}
