import userService from '@/services/user-service';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { message } from 'antd';

/**
 * Hook to fetch system configuration including register enable status
 * @returns System configuration with loading status
 */
export const useSystemConfig = () => {
  const { data, isLoading } = useQuery({
    queryKey: ['systemConfig'],
    queryFn: async () => {
      const { data = {} } = await userService.getSystemConfig();
      return data.data || { registerEnabled: 1 }; // Default to enabling registration
    },
  });

  return { config: data, loading: isLoading };
};

/**
 * Hook to fetch interface configuration
 * @returns Interface configuration with loading status
 */
export const useInterfaceConfig = () => {
  const { data, isLoading, refetch } = useQuery({
    queryKey: ['interfaceConfig'],
    queryFn: async () => {
      const { data = {} } = await userService.getInterfaceConfig();
      return (
        data.data || {
          logo: '',
          favicon: '',
          login_logo: '',
          login_welcome_text: '欢迎使用 RAGFlow\n智能知识管理与AI助手平台',
        }
      );
    },
  });

  return { config: data, loading: isLoading, refetch };
};

/**
 * Hook to save interface configuration
 * @returns Save interface configuration mutation
 */
export const useSaveInterfaceConfig = () => {
  const queryClient = useQueryClient();

  const { mutateAsync, isPending } = useMutation({
    mutationKey: ['saveInterfaceConfig'],
    mutationFn: async (config: {
      logo?: string;
      favicon?: string;
      login_logo?: string;
      login_welcome_text?: string;
    }) => {
      const { data = {} } = await userService.saveInterfaceConfig(config);
      return data;
    },
    onSuccess: (data) => {
      if (data.code === 0) {
        message.success('界面配置保存成功');
        // 刷新界面配置缓存
        queryClient.invalidateQueries({ queryKey: ['interfaceConfig'] });
      } else {
        message.error(data.message || '保存失败');
      }
    },
    onError: (error) => {
      message.error('保存失败');
      console.error('Save interface config error:', error);
    },
  });

  return { saveInterfaceConfig: mutateAsync, loading: isPending };
};

/**
 * Hook to upload interface file
 * @returns Upload interface file mutation
 */
export const useUploadInterfaceFile = () => {
  const queryClient = useQueryClient();

  const { mutateAsync, isPending } = useMutation({
    mutationKey: ['uploadInterfaceFile'],
    mutationFn: async (params: { file: File; type: string }) => {
      const formData = new FormData();
      formData.append('file', params.file);
      formData.append('type', params.type);

      const { data = {} } = await userService.uploadInterfaceFile(formData);
      return data;
    },
    onSuccess: (data) => {
      if (data.code === 0) {
        message.success('文件上传成功');
        // 刷新界面配置缓存，让页面上的logo立即更新
        queryClient.invalidateQueries({ queryKey: ['interfaceConfig'] });
      } else {
        message.error(data.message || '上传失败');
      }
    },
    onError: (error) => {
      message.error('上传失败');
      console.error('Upload interface file error:', error);
    },
  });

  return { uploadInterfaceFile: mutateAsync, loading: isPending };
};
