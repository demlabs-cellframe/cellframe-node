#!/usr/bin/env python3
"""
Mobile App Architecture Generator
Генератор архитектуры мобильного приложения для документации Cellframe API
Фаза 3 проекта документации - React Native/Flutter приложение
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional
import datetime

class MobileAppArchitecture:
    """Генератор архитектуры мобильного приложения"""
    
    def __init__(self, output_dir: str = ".context/mobile-app"):
        self.output_dir = Path(output_dir)
        self.app_name = "Cellframe API Docs"
        self.package_name = "com.cellframe.apidocs"
        
        # Конфигурация приложения
        self.config = {
            'platform': 'react-native',  # react-native или flutter
            'target_platforms': ['ios', 'android'],
            'offline_support': True,
            'search_engine': 'local',  # local или cloud
            'theme_support': True,
            'multilingual': True,
            'push_notifications': True,
            'analytics': True,
            'crash_reporting': True
        }
        
        # Архитектурные компоненты
        self.architecture = {
            'presentation': {
                'screens': [
                    'HomeScreen', 'SearchScreen', 'FunctionDetailScreen',
                    'CategoryScreen', 'BookmarksScreen', 'SettingsScreen',
                    'AboutScreen', 'OnboardingScreen'
                ],
                'components': [
                    'FunctionCard', 'SearchBar', 'CategoryFilter',
                    'CodeHighlighter', 'BookmarkButton', 'ShareButton'
                ],
                'navigation': 'react-navigation' if self.config['platform'] == 'react-native' else 'flutter-navigation'
            },
            'business_logic': {
                'services': [
                    'DocumentationService', 'SearchService', 'BookmarkService',
                    'SettingsService', 'AnalyticsService', 'NotificationService'
                ],
                'state_management': 'redux' if self.config['platform'] == 'react-native' else 'bloc',
                'data_models': [
                    'Function', 'Category', 'Bookmark', 'SearchResult', 'Settings'
                ]
            },
            'data_layer': {
                'local_storage': 'sqlite',
                'cache_strategy': 'lru_cache',
                'offline_storage': 'realm' if self.config['platform'] == 'react-native' else 'hive',
                'sync_mechanism': 'incremental_sync'
            },
            'infrastructure': {
                'build_system': 'metro' if self.config['platform'] == 'react-native' else 'gradle',
                'testing': 'jest' if self.config['platform'] == 'react-native' else 'flutter_test',
                'ci_cd': 'github_actions',
                'deployment': ['app_store', 'google_play', 'firebase_distribution']
            }
        }

    def generate_project_structure(self) -> Dict:
        """Генерирует структуру проекта мобильного приложения"""
        
        if self.config['platform'] == 'react-native':
            return self.generate_react_native_structure()
        else:
            return self.generate_flutter_structure()

    def generate_react_native_structure(self) -> Dict:
        """Генерирует структуру React Native проекта"""
        
        structure = {
            'package.json': self.generate_package_json(),
            'app.json': self.generate_app_config(),
            'metro.config.js': self.generate_metro_config(),
            'babel.config.js': self.generate_babel_config(),
            'src/': {
                'App.tsx': self.generate_app_component(),
                'navigation/': {
                    'AppNavigator.tsx': self.generate_app_navigator(),
                    'types.ts': self.generate_navigation_types()
                },
                'screens/': {
                    'HomeScreen.tsx': self.generate_home_screen(),
                    'SearchScreen.tsx': self.generate_search_screen(),
                    'FunctionDetailScreen.tsx': self.generate_function_detail_screen(),
                    'CategoryScreen.tsx': self.generate_category_screen(),
                    'BookmarksScreen.tsx': self.generate_bookmarks_screen(),
                    'SettingsScreen.tsx': self.generate_settings_screen()
                },
                'components/': {
                    'FunctionCard.tsx': self.generate_function_card(),
                    'SearchBar.tsx': self.generate_search_bar(),
                    'CodeHighlighter.tsx': self.generate_code_highlighter(),
                    'CategoryFilter.tsx': self.generate_category_filter()
                },
                'services/': {
                    'DocumentationService.ts': self.generate_documentation_service(),
                    'SearchService.ts': self.generate_search_service(),
                    'BookmarkService.ts': self.generate_bookmark_service(),
                    'AnalyticsService.ts': self.generate_analytics_service()
                },
                'store/': {
                    'index.ts': self.generate_store_config(),
                    'slices/': {
                        'documentationSlice.ts': self.generate_documentation_slice(),
                        'searchSlice.ts': self.generate_search_slice(),
                        'bookmarksSlice.ts': self.generate_bookmarks_slice()
                    }
                },
                'types/': {
                    'api.ts': self.generate_api_types(),
                    'navigation.ts': self.generate_navigation_types(),
                    'common.ts': self.generate_common_types()
                },
                'utils/': {
                    'constants.ts': self.generate_constants(),
                    'helpers.ts': self.generate_helpers(),
                    'storage.ts': self.generate_storage_utils()
                },
                'assets/': {
                    'images/': {},
                    'fonts/': {},
                    'data/': {
                        'api_functions.json': '// Локальная копия API функций'
                    }
                }
            },
            'android/': {
                'app/': {
                    'src/main/': {
                        'AndroidManifest.xml': self.generate_android_manifest(),
                        'res/': {
                            'values/': {
                                'strings.xml': self.generate_android_strings()
                            }
                        }
                    }
                }
            },
            'ios/': {
                'CellframeAPIDocs/': {
                    'Info.plist': self.generate_ios_info_plist()
                }
            },
            '__tests__/': {
                'App.test.tsx': self.generate_app_test(),
                'services/': {
                    'SearchService.test.ts': self.generate_search_service_test()
                }
            },
            '.github/workflows/': {
                'ci.yml': self.generate_github_actions_ci(),
                'release.yml': self.generate_github_actions_release()
            }
        }
        
        return structure

    def generate_package_json(self) -> str:
        """Генерирует package.json для React Native"""
        return json.dumps({
            "name": "cellframe-api-docs",
            "version": "1.0.0",
            "private": True,
            "scripts": {
                "start": "react-native start",
                "android": "react-native run-android",
                "ios": "react-native run-ios",
                "test": "jest",
                "lint": "eslint . --ext .js,.jsx,.ts,.tsx",
                "build:android": "cd android && ./gradlew assembleRelease",
                "build:ios": "cd ios && xcodebuild -workspace CellframeAPIDocs.xcworkspace -scheme CellframeAPIDocs -configuration Release -destination generic/platform=iOS -archivePath CellframeAPIDocs.xcarchive archive"
            },
            "dependencies": {
                "react": "18.2.0",
                "react-native": "0.72.6",
                "@react-navigation/native": "^6.1.9",
                "@react-navigation/stack": "^6.3.20",
                "@react-navigation/bottom-tabs": "^6.5.11",
                "@reduxjs/toolkit": "^1.9.7",
                "react-redux": "^8.1.3",
                "react-native-sqlite-storage": "^6.0.1",
                "react-native-vector-icons": "^10.0.2",
                "react-native-syntax-highlighter": "^2.1.0",
                "react-native-paper": "^5.11.1",
                "react-native-gesture-handler": "^2.13.4",
                "react-native-reanimated": "^3.5.4",
                "react-native-safe-area-context": "^4.7.4",
                "react-native-screens": "^3.27.0",
                "react-native-share": "^9.4.1",
                "react-native-device-info": "^10.11.0",
                "react-native-async-storage": "^1.19.5",
                "fuse.js": "^7.0.0",
                "react-native-push-notification": "^8.1.1"
            },
            "devDependencies": {
                "@babel/core": "^7.20.0",
                "@babel/preset-env": "^7.20.0",
                "@babel/runtime": "^7.20.0",
                "@react-native/eslint-config": "^0.72.2",
                "@react-native/metro-config": "^0.72.11",
                "@tsconfig/react-native": "^3.0.0",
                "@types/react": "^18.0.24",
                "@types/react-test-renderer": "^18.0.0",
                "babel-jest": "^29.2.1",
                "eslint": "^8.19.0",
                "jest": "^29.2.1",
                "metro-react-native-babel-preset": "0.76.8",
                "prettier": "^2.4.1",
                "react-test-renderer": "18.2.0",
                "typescript": "4.8.4"
            },
            "jest": {
                "preset": "react-native"
            }
        }, indent=2)

    def generate_app_config(self) -> str:
        """Генерирует app.json для React Native"""
        return json.dumps({
            "expo": {
                "name": "Cellframe API Docs",
                "slug": "cellframe-api-docs",
                "version": "1.0.0",
                "orientation": "portrait",
                "icon": "./assets/icon.png",
                "splash": {
                    "image": "./assets/splash.png",
                    "resizeMode": "contain",
                    "backgroundColor": "#2196F3"
                },
                "updates": {
                    "fallbackToCacheTimeout": 0
                },
                "assetBundlePatterns": ["**/*"],
                "ios": {
                    "supportsTablet": True,
                    "bundleIdentifier": "com.cellframe.apidocs"
                },
                "android": {
                    "adaptiveIcon": {
                        "foregroundImage": "./assets/adaptive-icon.png",
                        "backgroundColor": "#FFFFFF"
                    },
                    "package": "com.cellframe.apidocs"
                }
            }
        }, indent=2)

    def generate_metro_config(self) -> str:
        """Генерирует metro.config.js"""
        return '''const {getDefaultConfig} = require('expo/metro-config');

const config = getDefaultConfig(__dirname);

module.exports = config;'''

    def generate_babel_config(self) -> str:
        """Генерирует babel.config.js"""
        return '''module.exports = function(api) {
  api.cache(true);
  return {
    presets: ['babel-preset-expo'],
  };
};'''

    def generate_app_component(self) -> str:
        """Генерирует главный компонент приложения"""
        return '''import React from 'react';
import { Provider } from 'react-redux';
import { NavigationContainer } from '@react-navigation/native';
import { PaperProvider } from 'react-native-paper';
import { store } from './store';
import { AppNavigator } from './navigation/AppNavigator';
import { theme } from './utils/theme';

const App: React.FC = () => {
  return (
    <Provider store={store}>
      <PaperProvider theme={theme}>
        <NavigationContainer>
          <AppNavigator />
        </NavigationContainer>
      </PaperProvider>
    </Provider>
  );
};

export default App;'''

    def generate_home_screen(self) -> str:
        """Генерирует главный экран приложения"""
        return '''import React, { useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { useSelector, useDispatch } from 'react-redux';
import { Card, Title, Paragraph, Button } from 'react-native-paper';
import { RootState } from '../store';
import { loadDocumentation } from '../store/slices/documentationSlice';
import { FunctionCard } from '../components/FunctionCard';
import { CategoryFilter } from '../components/CategoryFilter';

export const HomeScreen: React.FC = () => {
  const navigation = useNavigation();
  const dispatch = useDispatch();
  
  const { 
    recentFunctions, 
    popularFunctions, 
    categories,
    isLoading 
  } = useSelector((state: RootState) => state.documentation);

  useEffect(() => {
    dispatch(loadDocumentation());
  }, [dispatch]);

  const navigateToSearch = () => {
    navigation.navigate('Search');
  };

  const navigateToCategory = (category: string) => {
    navigation.navigate('Category', { category });
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Title style={styles.title}>Cellframe API Documentation</Title>
        <Paragraph style={styles.subtitle}>
          Полная документация по API блокчейн платформы Cellframe
        </Paragraph>
        
        <Button 
          mode="contained" 
          onPress={navigateToSearch}
          style={styles.searchButton}
          icon="magnify"
        >
          Поиск функций
        </Button>
      </View>

      <View style={styles.section}>
        <Title style={styles.sectionTitle}>Категории</Title>
        <CategoryFilter 
          categories={categories}
          onCategorySelect={navigateToCategory}
        />
      </View>

      <View style={styles.section}>
        <Title style={styles.sectionTitle}>Популярные функции</Title>
        {popularFunctions.map((func) => (
          <FunctionCard 
            key={func.name}
            function={func}
            onPress={() => navigation.navigate('FunctionDetail', { functionName: func.name })}
          />
        ))}
      </View>

      <View style={styles.section}>
        <Title style={styles.sectionTitle}>Недавно просмотренные</Title>
        {recentFunctions.length > 0 ? (
          recentFunctions.map((func) => (
            <FunctionCard 
              key={func.name}
              function={func}
              onPress={() => navigation.navigate('FunctionDetail', { functionName: func.name })}
            />
          ))
        ) : (
          <Paragraph>Нет недавно просмотренных функций</Paragraph>
        )}
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    padding: 20,
    backgroundColor: '#2196F3',
    borderBottomLeftRadius: 20,
    borderBottomRightRadius: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: 'rgba(255, 255, 255, 0.8)',
    marginBottom: 20,
  },
  searchButton: {
    marginTop: 10,
  },
  section: {
    padding: 20,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 15,
    color: '#333',
  },
});'''

    def generate_search_screen(self) -> str:
        """Генерирует экран поиска"""
        return '''import React, { useState, useEffect } from 'react';
import {
  View,
  FlatList,
  StyleSheet,
} from 'react-native';
import { useSelector, useDispatch } from 'react-redux';
import { Searchbar, List, Text } from 'react-native-paper';
import { RootState } from '../store';
import { searchFunctions, clearSearch } from '../store/slices/searchSlice';
import { FunctionCard } from '../components/FunctionCard';
import { useNavigation } from '@react-navigation/native';

export const SearchScreen: React.FC = () => {
  const [query, setQuery] = useState('');
  const navigation = useNavigation();
  const dispatch = useDispatch();
  
  const { 
    results, 
    isLoading, 
    recentSearches 
  } = useSelector((state: RootState) => state.search);

  useEffect(() => {
    if (query.length > 2) {
      dispatch(searchFunctions(query));
    } else if (query.length === 0) {
      dispatch(clearSearch());
    }
  }, [query, dispatch]);

  const handleFunctionPress = (functionName: string) => {
    navigation.navigate('FunctionDetail', { functionName });
  };

  const renderFunction = ({ item }) => (
    <FunctionCard 
      function={item}
      onPress={() => handleFunctionPress(item.name)}
      showCategory={true}
    />
  );

  const renderRecentSearch = ({ item }) => (
    <List.Item
      title={item}
      left={props => <List.Icon {...props} icon="history" />}
      onPress={() => setQuery(item)}
    />
  );

  return (
    <View style={styles.container}>
      <Searchbar
        placeholder="Поиск функций API..."
        onChangeText={setQuery}
        value={query}
        style={styles.searchbar}
        loading={isLoading}
      />

      {query.length === 0 && recentSearches.length > 0 && (
        <View style={styles.recentSearches}>
          <Text style={styles.sectionTitle}>Недавние поиски</Text>
          <FlatList
            data={recentSearches}
            renderItem={renderRecentSearch}
            keyExtractor={(item, index) => index.toString()}
          />
        </View>
      )}

      {results.length > 0 && (
        <FlatList
          data={results}
          renderItem={renderFunction}
          keyExtractor={item => item.name}
          style={styles.results}
          showsVerticalScrollIndicator={false}
        />
      )}

      {query.length > 2 && results.length === 0 && !isLoading && (
        <View style={styles.noResults}>
          <Text>Функции не найдены</Text>
          <Text style={styles.noResultsHint}>
            Попробуйте изменить запрос или проверьте правописание
          </Text>
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  searchbar: {
    margin: 16,
    elevation: 4,
  },
  recentSearches: {
    backgroundColor: 'white',
    margin: 16,
    borderRadius: 8,
    padding: 16,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  results: {
    flex: 1,
    paddingHorizontal: 16,
  },
  noResults: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 32,
  },
  noResultsHint: {
    textAlign: 'center',
    color: '#666',
    marginTop: 8,
  },
});'''

    def generate_function_detail_screen(self) -> str:
        """Генерирует экран детального просмотра функции"""
        return '''import React, { useEffect, useState } from 'react';
import {
  View,
  ScrollView,
  StyleSheet,
  Share,
} from 'react-native';
import { useRoute, useNavigation } from '@react-navigation/native';
import { 
  Title, 
  Paragraph, 
  Card, 
  Button, 
  Chip,
  IconButton,
  Divider 
} from 'react-native-paper';
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '../store';
import { loadFunctionDetail } from '../store/slices/documentationSlice';
import { toggleBookmark } from '../store/slices/bookmarksSlice';
import { CodeHighlighter } from '../components/CodeHighlighter';

export const FunctionDetailScreen: React.FC = () => {
  const route = useRoute();
  const navigation = useNavigation();
  const dispatch = useDispatch();
  
  const { functionName } = route.params;
  
  const { currentFunction, isLoading } = useSelector(
    (state: RootState) => state.documentation
  );
  
  const { bookmarks } = useSelector(
    (state: RootState) => state.bookmarks
  );
  
  const isBookmarked = bookmarks.some(b => b.name === functionName);

  useEffect(() => {
    dispatch(loadFunctionDetail(functionName));
    
    navigation.setOptions({
      title: functionName,
      headerRight: () => (
        <View style={styles.headerButtons}>
          <IconButton
            icon={isBookmarked ? 'bookmark' : 'bookmark-outline'}
            onPress={() => dispatch(toggleBookmark(currentFunction))}
          />
          <IconButton
            icon="share"
            onPress={handleShare}
          />
        </View>
      ),
    });
  }, [functionName, isBookmarked]);

  const handleShare = async () => {
    if (currentFunction) {
      try {
        await Share.share({
          message: `Проверьте эту функцию Cellframe API: ${currentFunction.name}\\n\\n${currentFunction.description}`,
          title: `Cellframe API: ${currentFunction.name}`,
        });
      } catch (error) {
        console.error('Ошибка при попытке поделиться:', error);
      }
    }
  };

  if (isLoading || !currentFunction) {
    return (
      <View style={styles.loading}>
        <Paragraph>Загрузка...</Paragraph>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <Card style={styles.card}>
        <Card.Content>
          <View style={styles.header}>
            <Title style={styles.functionName}>{currentFunction.name}</Title>
            <Chip mode="outlined" style={styles.categoryChip}>
              {currentFunction.category}
            </Chip>
          </View>
          
          <Paragraph style={styles.description}>
            {currentFunction.description}
          </Paragraph>
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Content>
          <Title style={styles.sectionTitle}>Сигнатура</Title>
          <CodeHighlighter
            code={currentFunction.signature}
            language="c"
          />
        </Card.Content>
      </Card>

      {currentFunction.parameters && currentFunction.parameters.length > 0 && (
        <Card style={styles.card}>
          <Card.Content>
            <Title style={styles.sectionTitle}>Параметры</Title>
            {currentFunction.parameters.map((param, index) => (
              <View key={index} style={styles.parameter}>
                <Title style={styles.parameterName}>{param.name}</Title>
                <Paragraph style={styles.parameterType}>{param.type}</Paragraph>
                <Paragraph>{param.description}</Paragraph>
                {index < currentFunction.parameters.length - 1 && (
                  <Divider style={styles.parameterDivider} />
                )}
              </View>
            ))}
          </Card.Content>
        </Card>
      )}

      <Card style={styles.card}>
        <Card.Content>
          <Title style={styles.sectionTitle}>Примеры использования</Title>
          
          <Title style={styles.exampleTitle}>C/C++</Title>
          <CodeHighlighter
            code={currentFunction.examples?.c || '// Пример будет добавлен'}
            language="c"
          />
          
          <Title style={styles.exampleTitle}>Python</Title>
          <CodeHighlighter
            code={currentFunction.examples?.python || '# Пример будет добавлен'}
            language="python"
          />
        </Card.Content>
      </Card>

      {currentFunction.relatedFunctions && currentFunction.relatedFunctions.length > 0 && (
        <Card style={styles.card}>
          <Card.Content>
            <Title style={styles.sectionTitle}>Связанные функции</Title>
            {currentFunction.relatedFunctions.map((relatedFunc, index) => (
              <Button
                key={index}
                mode="outlined"
                style={styles.relatedButton}
                onPress={() => navigation.push('FunctionDetail', { functionName: relatedFunc })}
              >
                {relatedFunc}
              </Button>
            ))}
          </Card.Content>
        </Card>
      )}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  loading: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  card: {
    margin: 16,
    marginBottom: 8,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 16,
  },
  functionName: {
    flex: 1,
    fontSize: 24,
    fontWeight: 'bold',
  },
  categoryChip: {
    marginLeft: 8,
  },
  description: {
    fontSize: 16,
    lineHeight: 24,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 12,
  },
  parameter: {
    marginBottom: 16,
  },
  parameterName: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  parameterType: {
    fontSize: 14,
    color: '#666',
    fontFamily: 'monospace',
  },
  parameterDivider: {
    marginTop: 8,
  },
  exampleTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginTop: 16,
    marginBottom: 8,
  },
  relatedButton: {
    marginBottom: 8,
  },
  headerButtons: {
    flexDirection: 'row',
  },
});'''

    def generate_documentation_service(self) -> str:
        """Генерирует сервис для работы с документацией"""
        return '''import AsyncStorage from '@react-native-async-storage/async-storage';
import { ApiFunction, Category } from '../types/api';

export class DocumentationService {
  private static instance: DocumentationService;
  private cache: Map<string, any> = new Map();
  private readonly CACHE_KEY = 'cellframe_api_docs';

  static getInstance(): DocumentationService {
    if (!DocumentationService.instance) {
      DocumentationService.instance = new DocumentationService();
    }
    return DocumentationService.instance;
  }

  async loadAllFunctions(): Promise<ApiFunction[]> {
    try {
      const cachedData = await AsyncStorage.getItem(this.CACHE_KEY);
      if (cachedData) {
        const data = JSON.parse(cachedData);
        return data.functions || [];
      }

      // Загрузка из локального файла
      const localData = require('../assets/data/api_functions.json');
      await this.cacheData(localData);
      
      return localData.functions || [];
    } catch (error) {
      console.error('Ошибка загрузки функций:', error);
      return [];
    }
  }

  async getFunctionByName(name: string): Promise<ApiFunction | null> {
    try {
      const functions = await this.loadAllFunctions();
      return functions.find(func => func.name === name) || null;
    } catch (error) {
      console.error('Ошибка получения функции:', error);
      return null;
    }
  }

  async getFunctionsByCategory(category: string): Promise<ApiFunction[]> {
    try {
      const functions = await this.loadAllFunctions();
      return functions.filter(func => func.category === category);
    } catch (error) {
      console.error('Ошибка получения функций по категории:', error);
      return [];
    }
  }

  async getCategories(): Promise<Category[]> {
    try {
      const functions = await this.loadAllFunctions();
      const categoryMap = new Map<string, Category>();

      functions.forEach(func => {
        if (!categoryMap.has(func.category)) {
          categoryMap.set(func.category, {
            name: func.category,
            displayName: this.formatCategoryName(func.category),
            count: 0,
            description: this.getCategoryDescription(func.category)
          });
        }
        const category = categoryMap.get(func.category)!;
        category.count++;
      });

      return Array.from(categoryMap.values()).sort((a, b) => b.count - a.count);
    } catch (error) {
      console.error('Ошибка получения категорий:', error);
      return [];
    }
  }

  async getPopularFunctions(): Promise<ApiFunction[]> {
    try {
      const functions = await this.loadAllFunctions();
      // Простая эвристика - функции с высоким приоритетом
      return functions
        .filter(func => func.priority && func.priority > 80)
        .sort((a, b) => (b.priority || 0) - (a.priority || 0))
        .slice(0, 10);
    } catch (error) {
      console.error('Ошибка получения популярных функций:', error);
      return [];
    }
  }

  async getRecentFunctions(): Promise<ApiFunction[]> {
    try {
      const recentNames = await AsyncStorage.getItem('recent_functions');
      if (!recentNames) return [];

      const names = JSON.parse(recentNames);
      const functions = await this.loadAllFunctions();
      
      return names
        .map(name => functions.find(func => func.name === name))
        .filter(func => func !== undefined)
        .slice(0, 5);
    } catch (error) {
      console.error('Ошибка получения недавних функций:', error);
      return [];
    }
  }

  async addToRecentFunctions(functionName: string): Promise<void> {
    try {
      const recentNames = await AsyncStorage.getItem('recent_functions');
      let names = recentNames ? JSON.parse(recentNames) : [];
      
      // Удаляем если уже есть
      names = names.filter(name => name !== functionName);
      
      // Добавляем в начало
      names.unshift(functionName);
      
      // Ограничиваем размер
      names = names.slice(0, 10);
      
      await AsyncStorage.setItem('recent_functions', JSON.stringify(names));
    } catch (error) {
      console.error('Ошибка добавления в недавние:', error);
    }
  }

  private async cacheData(data: any): Promise<void> {
    try {
      await AsyncStorage.setItem(this.CACHE_KEY, JSON.stringify(data));
    } catch (error) {
      console.error('Ошибка кэширования данных:', error);
    }
  }

  private formatCategoryName(category: string): string {
    return category
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  }

  private getCategoryDescription(category: string): string {
    const descriptions = {
      'critical_core': 'Критические функции ядра системы',
      'blockchain_operations': 'Операции с блокчейном',
      'network_layer': 'Сетевые коммуникации',
      'cryptography': 'Криптографические операции',
      'data_structures': 'Структуры данных',
      'utilities': 'Вспомогательные функции',
      'testing_debug': 'Тестирование и отладка',
      'legacy_deprecated': 'Устаревшие функции'
    };
    
    return descriptions[category] || 'Функции категории ' + this.formatCategoryName(category);
  }
}'''

    def generate_github_actions_ci(self) -> str:
        """Генерирует GitHub Actions для CI/CD"""
        return '''name: Mobile App CI

on:
  push:
    branches: [ main, develop ]
    paths:
      - 'mobile-app/**'
  pull_request:
    branches: [ main ]
    paths:
      - 'mobile-app/**'

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'
        cache-dependency-path: mobile-app/package-lock.json
    
    - name: Install dependencies
      working-directory: mobile-app
      run: npm ci
    
    - name: Run tests
      working-directory: mobile-app
      run: npm test -- --coverage --watchAll=false
    
    - name: Run linting
      working-directory: mobile-app
      run: npm run lint
    
    - name: Type checking
      working-directory: mobile-app
      run: npx tsc --noEmit

  build-android:
    runs-on: ubuntu-latest
    needs: test
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'
        cache-dependency-path: mobile-app/package-lock.json
    
    - name: Setup Java
      uses: actions/setup-java@v3
      with:
        distribution: 'temurin'
        java-version: '17'
    
    - name: Install dependencies
      working-directory: mobile-app
      run: npm ci
    
    - name: Build Android APK
      working-directory: mobile-app
      run: |
        cd android
        ./gradlew assembleRelease
    
    - name: Upload APK
      uses: actions/upload-artifact@v3
      with:
        name: android-apk
        path: mobile-app/android/app/build/outputs/apk/release/

  build-ios:
    runs-on: macos-latest
    needs: test
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'
        cache-dependency-path: mobile-app/package-lock.json
    
    - name: Install dependencies
      working-directory: mobile-app
      run: npm ci
    
    - name: Install CocoaPods
      working-directory: mobile-app/ios
      run: pod install
    
    - name: Build iOS
      working-directory: mobile-app
      run: |
        cd ios
        xcodebuild -workspace CellframeAPIDocs.xcworkspace \\
                   -scheme CellframeAPIDocs \\
                   -configuration Release \\
                   -destination generic/platform=iOS \\
                   -archivePath CellframeAPIDocs.xcarchive \\
                   archive
    
    - name: Upload iOS Archive
      uses: actions/upload-artifact@v3
      with:
        name: ios-archive
        path: mobile-app/ios/CellframeAPIDocs.xcarchive'''

    def create_mobile_app_files(self) -> bool:
        """Создает файлы мобильного приложения"""
        try:
            structure = self.generate_project_structure()
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
            return self._create_files_from_structure(structure, self.output_dir)
            
        except Exception as e:
            print(f"❌ Ошибка создания файлов мобильного приложения: {e}")
            return False

    def _create_files_from_structure(self, structure: Dict, base_path: Path) -> bool:
        """Рекурсивно создает файлы из структуры"""
        try:
            for name, content in structure.items():
                path = base_path / name
                
                if isinstance(content, dict):
                    # Это директория
                    path.mkdir(parents=True, exist_ok=True)
                    self._create_files_from_structure(content, path)
                else:
                    # Это файл
                    path.parent.mkdir(parents=True, exist_ok=True)
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(content)
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка создания файла {path}: {e}")
            return False

    def generate_app_architecture_report(self) -> Dict:
        """Генерирует отчет об архитектуре приложения"""
        return {
            'app_info': {
                'name': self.app_name,
                'package_name': self.package_name,
                'platform': self.config['platform'],
                'target_platforms': self.config['target_platforms']
            },
            'features': {
                'offline_support': self.config['offline_support'],
                'search_engine': self.config['search_engine'],
                'theme_support': self.config['theme_support'],
                'multilingual': self.config['multilingual'],
                'push_notifications': self.config['push_notifications'],
                'analytics': self.config['analytics']
            },
            'architecture': self.architecture,
            'estimated_development_time': {
                'design_phase': '2 weeks',
                'development_phase': '6 weeks',
                'testing_phase': '2 weeks',
                'deployment_phase': '1 week',
                'total': '11 weeks'
            },
            'resource_requirements': {
                'mobile_developers': 2,
                'ui_ux_designer': 1,
                'qa_engineer': 1,
                'project_manager': 1
            },
            'technical_specifications': {
                'minimum_android_version': '6.0 (API 23)',
                'minimum_ios_version': '12.0',
                'storage_requirements': '50 MB',
                'offline_storage': '200 MB',
                'supported_languages': ['Russian', 'English', 'Chinese']
            }
        }

def main():
    """Главная функция для создания архитектуры мобильного приложения"""
    generator = MobileAppArchitecture()
    
    print("🚀 Создание архитектуры мобильного приложения Cellframe API Docs...")
    
    # Создаем файлы приложения
    if generator.create_mobile_app_files():
        print("✅ Файлы мобильного приложения созданы успешно")
    else:
        print("❌ Ошибка создания файлов мобильного приложения")
        return 1
    
    # Генерируем отчет об архитектуре
    report = generator.generate_app_architecture_report()
    
    # Сохраняем отчет
    report_file = Path(".context/analysis/mobile_app_architecture_report.json")
    report_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"📋 Отчет об архитектуре сохранен: {report_file}")
    print(f"📱 Мобильное приложение: {generator.config['platform'].upper()}")
    print(f"🎯 Целевые платформы: {', '.join(generator.config['target_platforms'])}")
    print(f"⚡ Функции: Оффлайн поиск, темы, уведомления, аналитика")
    
    return 0

if __name__ == '__main__':
    exit(main()) 