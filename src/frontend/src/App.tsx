import { Provider } from 'react-redux';
import { PersistGate } from 'redux-persist/integration/react';
import { RouterProvider } from 'react-router-dom';
import { store, persistor } from './store';
import router from './router';
import LoadingSpinner from './components/common/LoadingSpinner';
import ThemeProvider from './components/providers/ThemeProvider';
import AuthProvider from './components/auth/AuthProvider';
import './styles/global.css';
import 'antd/dist/reset.css';

function App() {
  return (
    <Provider store={store}>
      <PersistGate loading={<LoadingSpinner />} persistor={persistor}>
        <AuthProvider>
          <ThemeProvider>
            <RouterProvider router={router} />
          </ThemeProvider>
        </AuthProvider>
      </PersistGate>
    </Provider>
  );
}

export default App;
