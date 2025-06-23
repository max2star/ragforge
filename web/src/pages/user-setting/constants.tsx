import { LLMFactory } from '@/constants/llm';
import { UserSettingRouteKey } from '@/constants/setting';
import {
  ApartmentOutlined,
  ApiOutlined,
  LockOutlined,
  LogoutOutlined,
  SettingOutlined,
  TeamOutlined,
  UserOutlined,
} from '@ant-design/icons';

export const UserSettingIconMap = {
  [UserSettingRouteKey.Profile]: <UserOutlined style={{ fontSize: 16 }} />,
  [UserSettingRouteKey.Password]: <LockOutlined style={{ fontSize: 16 }} />,
  [UserSettingRouteKey.Model]: <ApartmentOutlined style={{ fontSize: 16 }} />,
  [UserSettingRouteKey.System]: <SettingOutlined style={{ fontSize: 16 }} />,
  [UserSettingRouteKey.Team]: <TeamOutlined style={{ fontSize: 16 }} />,
  [UserSettingRouteKey.Logout]: <LogoutOutlined style={{ fontSize: 16 }} />,
  [UserSettingRouteKey.Api]: <ApiOutlined style={{ fontSize: 16 }} />,
};

export * from '@/constants/setting';

export const LocalLlmFactories = [
  LLMFactory.Ollama,
  LLMFactory.Xinference,
  LLMFactory.LocalAI,
  LLMFactory.LMStudio,
  LLMFactory.OpenAiAPICompatible,
  LLMFactory.TogetherAI,
  LLMFactory.Replicate,
  LLMFactory.OpenRouter,
  LLMFactory.HuggingFace,
  LLMFactory.GPUStack,
  LLMFactory.ModelScope,
  LLMFactory.VLLM,
];

export enum TenantRole {
  Owner = 'owner',
  Invite = 'invite',
  Normal = 'normal',
}
