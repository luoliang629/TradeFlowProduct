import { useDispatch, useSelector } from 'react-redux';
import type { TypedUseSelectorHook } from 'react-redux';
import type { RootState, AppDispatch } from './index';

// 类型安全的hooks
export const useAppDispatch = () => useDispatch<AppDispatch>();
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;

// 常用的选择器hooks
export const useAuth = () => useAppSelector(state => state.auth);
export const useChat = () => useAppSelector(state => state.chat);
export const useUI = () => useAppSelector(state => state.ui);