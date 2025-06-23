import {
  ApiIcon,
  LogOutIcon,
  ModelProviderIcon,
  PasswordIcon,
  ProfileIcon,
  TeamIcon,
} from '@/assets/icon/Icon';
import { LLMFactory } from '@/constants/llm';
import { UserSettingRouteKey } from '@/constants/setting';
import { MonitorOutlined } from '@ant-design/icons';

export const UserSettingIconMap = {
  [UserSettingRouteKey.Profile]: <ProfileIcon style={{ fontSize: 20 }} />,
  [UserSettingRouteKey.Password]: <PasswordIcon style={{ fontSize: 20 }} />,
  [UserSettingRouteKey.Model]: <ModelProviderIcon style={{ fontSize: 20 }} />,
  [UserSettingRouteKey.System]: <MonitorOutlined style={{ fontSize: 20 }} />,
  [UserSettingRouteKey.Team]: <TeamIcon style={{ fontSize: 20 }} />,
  [UserSettingRouteKey.Logout]: <LogOutIcon style={{ fontSize: 20 }} />,
  [UserSettingRouteKey.Api]: <ApiIcon style={{ fontSize: 20 }} />,
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
