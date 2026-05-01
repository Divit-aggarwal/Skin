import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { usersApi, UpdateProfileData } from '../api/users';
import { useUserStore } from '../store/userStore';

export function useProfile() {
  const setUser = useUserStore((s) => s.setUser);
  const setProfile = useUserStore((s) => s.setProfile);

  return useQuery({
    queryKey: ['profile'],
    queryFn: async () => {
      const [meRes, profileRes] = await Promise.all([
        usersApi.getMe(),
        usersApi.getProfile(),
      ]);
      setUser({ id: meRes.data.id, email: meRes.data.email });
      setProfile({
        display_name: profileRes.data.display_name,
        age: profileRes.data.age,
        gender: profileRes.data.gender,
        skin_type: profileRes.data.skin_type,
      });
      return { user: meRes.data, profile: profileRes.data };
    },
    staleTime: 5 * 60 * 1000,
  });
}

export function useUpdateProfile() {
  const queryClient = useQueryClient();
  const setProfile = useUserStore((s) => s.setProfile);

  return useMutation({
    mutationFn: (data: UpdateProfileData) => usersApi.updateProfile(data),
    onSuccess: (res) => {
      setProfile({
        display_name: res.data.display_name,
        age: res.data.age,
        gender: res.data.gender,
        skin_type: res.data.skin_type,
      });
      queryClient.invalidateQueries({ queryKey: ['profile'] });
    },
  });
}
