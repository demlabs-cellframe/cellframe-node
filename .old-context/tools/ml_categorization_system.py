#!/usr/bin/env python3
"""
ML Categorization System
Система машинного обучения для автоматической категоризации функций Cellframe API
Фаза 3 проекта документации
"""

import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib
import datetime

class MLCategorizationSystem:
    """Система ML для автоматической категоризации функций API"""
    
    def __init__(self, model_dir: str = ".context/ml-models"):
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        
        # Модели
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 3),
            lowercase=True
        )
        self.classifier = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        
        # Категории с весами важности
        self.categories = {
            'critical_core': {
                'weight': 100,
                'keywords': [
                    'init', 'deinit', 'create', 'destroy', 'alloc', 'free',
                    'start', 'stop', 'main', 'core', 'system', 'global'
                ],
                'patterns': [
                    r'.*_init$', r'.*_deinit$', r'.*_create$', r'.*_destroy$',
                    r'^dap_common_.*', r'^dap_config_.*', r'^dap_proc_.*'
                ]
            },
            'blockchain_operations': {
                'weight': 95,
                'keywords': [
                    'chain', 'block', 'ledger', 'transaction', 'tx', 'consensus',
                    'mining', 'stake', 'validator', 'node', 'sync'
                ],
                'patterns': [
                    r'^dap_chain_.*', r'^dap_ledger_.*', r'^dap_consensus_.*',
                    r'.*_block_.*', r'.*_tx_.*', r'.*_transaction_.*'
                ]
            },
            'network_layer': {
                'weight': 85,
                'keywords': [
                    'net', 'network', 'stream', 'client', 'server', 'http',
                    'socket', 'connection', 'peer', 'protocol', 'packet'
                ],
                'patterns': [
                    r'^dap_stream_.*', r'^dap_client_.*', r'^dap_server_.*',
                    r'^dap_http_.*', r'.*_net_.*', r'.*_peer_.*'
                ]
            },
            'cryptography': {
                'weight': 90,
                'keywords': [
                    'crypto', 'hash', 'sign', 'verify', 'encrypt', 'decrypt',
                    'key', 'cert', 'pkey', 'signature', 'cipher'
                ],
                'patterns': [
                    r'^dap_enc_.*', r'^dap_hash_.*', r'^dap_sign_.*',
                    r'^dap_crypto_.*', r'.*_key_.*', r'.*_cert_.*'
                ]
            },
            'data_structures': {
                'weight': 75,
                'keywords': [
                    'list', 'hash_table', 'tree', 'queue', 'stack', 'array',
                    'buffer', 'string', 'memory', 'data'
                ],
                'patterns': [
                    r'^dap_list_.*', r'^dap_hash_table_.*', r'^dap_tree_.*',
                    r'^dap_string_.*', r'.*_list_.*', r'.*_array_.*'
                ]
            },
            'python_integration': {
                'weight': 80,
                'keywords': [
                    'python', 'py', 'init', 'module', 'object', 'method',
                    'wrapper', 'binding', 'api'
                ],
                'patterns': [
                    r'^PyInit_.*', r'^py_.*', r'.*_python_.*',
                    r'.*_py_.*', r'.*_wrapper_.*'
                ]
            },
            'utilities': {
                'weight': 60,
                'keywords': [
                    'util', 'helper', 'tool', 'format', 'convert', 'parse',
                    'validate', 'check', 'get', 'set', 'find'
                ],
                'patterns': [
                    r'^dap_.*_get$', r'^dap_.*_set$', r'^dap_.*_find$',
                    r'.*_util_.*', r'.*_helper_.*', r'.*_tool_.*'
                ]
            },
            'testing_debug': {
                'weight': 30,
                'keywords': [
                    'test', 'debug', 'mock', 'stub', 'trace', 'log',
                    'print', 'dump', 'check', 'assert'
                ],
                'patterns': [
                    r'.*test.*', r'.*debug.*', r'.*mock.*',
                    r'.*_print$', r'.*_dump$', r'.*_trace$'
                ]
            }
        }
        
        # Обученные модели
        self.is_trained = False
        self.training_accuracy = 0.0
        self.feature_importance = {}

    def extract_features(self, function_data: Dict) -> str:
        """Извлекает признаки из данных функции"""
        features = []
        
        # Название функции
        name = function_data.get('name', '')
        features.append(name)
        
        # Сигнатура
        signature = function_data.get('signature', '')
        features.append(signature)
        
        # Комментарии
        comments = ' '.join(function_data.get('comments', []))
        features.append(comments)
        
        # Модуль
        module = function_data.get('module', '')
        features.append(module)
        
        # Параметры
        params = function_data.get('parameters', [])
        param_types = ' '.join([p.get('type', '') for p in params])
        features.append(param_types)
        
        # Возвращаемый тип
        return_type = function_data.get('return_type', '')
        features.append(return_type)
        
        return ' '.join(features).lower()

    def rule_based_categorization(self, function_data: Dict) -> Tuple[str, float]:
        """Категоризация на основе правил"""
        name = function_data.get('name', '').lower()
        module = function_data.get('module', '').lower()
        signature = function_data.get('signature', '').lower()
        
        best_category = 'utilities'
        best_score = 0.0
        
        for category, config in self.categories.items():
            score = 0.0
            
            # Проверяем паттерны
            for pattern in config['patterns']:
                if re.match(pattern, name, re.IGNORECASE):
                    score += config['weight'] * 0.8
                    break
            
            # Проверяем ключевые слова
            keyword_matches = 0
            for keyword in config['keywords']:
                if keyword in name or keyword in module or keyword in signature:
                    keyword_matches += 1
            
            if keyword_matches > 0:
                score += (keyword_matches / len(config['keywords'])) * config['weight'] * 0.6
            
            # Нормализуем оценку
            score = min(score, 100.0)
            
            if score > best_score:
                best_score = score
                best_category = category
        
        return best_category, best_score / 100.0

    def prepare_training_data(self, api_data: Dict) -> Tuple[List[str], List[str]]:
        """Подготавливает данные для обучения"""
        features = []
        labels = []
        
        for module_name, module_data in api_data.get('modules', {}).items():
            for function in module_data.get('functions', []):
                # Извлекаем признаки
                feature_text = self.extract_features(function)
                features.append(feature_text)
                
                # Получаем категорию (используем rule-based как ground truth)
                category, confidence = self.rule_based_categorization(function)
                labels.append(category)
        
        return features, labels

    def train_model(self, api_data: Dict) -> Dict:
        """Обучает модель машинного обучения"""
        print("🤖 Обучение модели категоризации...")
        
        # Подготавливаем данные
        features, labels = self.prepare_training_data(api_data)
        
        if len(features) < 10:
            raise ValueError("Недостаточно данных для обучения (минимум 10 функций)")
        
        # Векторизация текста
        X = self.vectorizer.fit_transform(features)
        y = np.array(labels)
        
        # Разделяем на обучающую и тестовую выборки
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Обучаем модель
        self.classifier.fit(X_train, y_train)
        
        # Оценка качества
        y_pred = self.classifier.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        report = classification_report(y_test, y_pred, output_dict=True)
        
        # Важность признаков
        feature_names = self.vectorizer.get_feature_names_out()
        importance_scores = self.classifier.feature_importances_
        
        # Топ-20 важных признаков
        top_indices = np.argsort(importance_scores)[-20:]
        self.feature_importance = {
            feature_names[i]: float(importance_scores[i]) 
            for i in top_indices
        }
        
        self.is_trained = True
        self.training_accuracy = accuracy
        
        # Сохраняем модели
        self.save_models()
        
        training_report = {
            'accuracy': accuracy,
            'classification_report': report,
            'feature_importance': self.feature_importance,
            'training_samples': len(features),
            'categories': list(self.categories.keys()),
            'timestamp': datetime.datetime.now().isoformat()
        }
        
        print(f"✅ Модель обучена с точностью: {accuracy:.3f}")
        return training_report

    def predict_category(self, function_data: Dict) -> Tuple[str, float, Dict]:
        """Предсказывает категорию функции"""
        if not self.is_trained:
            # Используем rule-based подход
            category, confidence = self.rule_based_categorization(function_data)
            return category, confidence, {'method': 'rule_based'}
        
        # Извлекаем признаки
        feature_text = self.extract_features(function_data)
        
        # Векторизация
        X = self.vectorizer.transform([feature_text])
        
        # Предсказание
        prediction = self.classifier.predict(X)[0]
        probabilities = self.classifier.predict_proba(X)[0]
        
        # Находим индекс предсказанной категории
        categories = self.classifier.classes_
        pred_index = np.where(categories == prediction)[0][0]
        confidence = probabilities[pred_index]
        
        # Дополнительная информация
        details = {
            'method': 'ml_model',
            'all_probabilities': {
                cat: float(prob) for cat, prob in zip(categories, probabilities)
            },
            'top_features': self.get_top_features_for_prediction(feature_text)
        }
        
        return prediction, confidence, details

    def get_top_features_for_prediction(self, feature_text: str, top_n: int = 5) -> List[str]:
        """Получает топ признаки для предсказания"""
        try:
            X = self.vectorizer.transform([feature_text])
            feature_names = self.vectorizer.get_feature_names_out()
            
            # Получаем ненулевые признаки
            nonzero_indices = X.nonzero()[1]
            feature_scores = [(feature_names[i], X[0, i]) for i in nonzero_indices]
            
            # Сортируем по важности
            feature_scores.sort(key=lambda x: x[1], reverse=True)
            
            return [feature for feature, score in feature_scores[:top_n]]
        except:
            return []

    def categorize_functions_batch(self, functions: List[Dict]) -> List[Dict]:
        """Категоризирует пакет функций"""
        results = []
        
        for function in functions:
            category, confidence, details = self.predict_category(function)
            
            result = {
                'function': function,
                'predicted_category': category,
                'confidence': confidence,
                'prediction_details': details
            }
            
            results.append(result)
        
        return results

    def save_models(self):
        """Сохраняет обученные модели"""
        try:
            # Сохраняем векторизатор
            joblib.dump(self.vectorizer, self.model_dir / 'vectorizer.pkl')
            
            # Сохраняем классификатор
            joblib.dump(self.classifier, self.model_dir / 'classifier.pkl')
            
            # Сохраняем метаданные
            metadata = {
                'is_trained': self.is_trained,
                'training_accuracy': self.training_accuracy,
                'feature_importance': self.feature_importance,
                'categories': list(self.categories.keys()),
                'saved_at': datetime.datetime.now().isoformat()
            }
            
            with open(self.model_dir / 'metadata.json', 'w') as f:
                json.dump(metadata, f, indent=2)
            
            print(f"💾 Модели сохранены в {self.model_dir}")
            
        except Exception as e:
            print(f"❌ Ошибка сохранения моделей: {e}")

    def load_models(self) -> bool:
        """Загружает сохраненные модели"""
        try:
            # Загружаем векторизатор
            self.vectorizer = joblib.load(self.model_dir / 'vectorizer.pkl')
            
            # Загружаем классификатор
            self.classifier = joblib.load(self.model_dir / 'classifier.pkl')
            
            # Загружаем метаданные
            with open(self.model_dir / 'metadata.json', 'r') as f:
                metadata = json.load(f)
            
            self.is_trained = metadata.get('is_trained', False)
            self.training_accuracy = metadata.get('training_accuracy', 0.0)
            self.feature_importance = metadata.get('feature_importance', {})
            
            print(f"📦 Модели загружены (точность: {self.training_accuracy:.3f})")
            return True
            
        except Exception as e:
            print(f"⚠️ Не удалось загрузить модели: {e}")
            return False

    def evaluate_categorization_quality(self, test_functions: List[Dict]) -> Dict:
        """Оценивает качество категоризации"""
        results = self.categorize_functions_batch(test_functions)
        
        # Статистика по категориям
        category_stats = {}
        confidence_scores = []
        
        for result in results:
            category = result['predicted_category']
            confidence = result['confidence']
            
            if category not in category_stats:
                category_stats[category] = {
                    'count': 0,
                    'avg_confidence': 0.0,
                    'confidences': []
                }
            
            category_stats[category]['count'] += 1
            category_stats[category]['confidences'].append(confidence)
            confidence_scores.append(confidence)
        
        # Вычисляем средние значения
        for category in category_stats:
            confidences = category_stats[category]['confidences']
            category_stats[category]['avg_confidence'] = np.mean(confidences)
            category_stats[category]['std_confidence'] = np.std(confidences)
        
        evaluation = {
            'total_functions': len(test_functions),
            'avg_confidence': np.mean(confidence_scores),
            'std_confidence': np.std(confidence_scores),
            'category_distribution': category_stats,
            'high_confidence_ratio': len([c for c in confidence_scores if c > 0.8]) / len(confidence_scores),
            'low_confidence_ratio': len([c for c in confidence_scores if c < 0.5]) / len(confidence_scores),
            'model_accuracy': self.training_accuracy,
            'evaluation_timestamp': datetime.datetime.now().isoformat()
        }
        
        return evaluation

    def generate_categorization_report(self, functions: List[Dict]) -> Dict:
        """Генерирует отчет о категоризации"""
        results = self.categorize_functions_batch(functions)
        evaluation = self.evaluate_categorization_quality(functions)
        
        report = {
            'summary': {
                'total_functions_categorized': len(functions),
                'model_used': 'ml_model' if self.is_trained else 'rule_based',
                'average_confidence': evaluation['avg_confidence'],
                'high_confidence_predictions': evaluation['high_confidence_ratio'] * 100
            },
            'category_breakdown': evaluation['category_distribution'],
            'quality_metrics': {
                'model_accuracy': self.training_accuracy,
                'prediction_confidence': evaluation['avg_confidence'],
                'confidence_std': evaluation['std_confidence']
            },
            'recommendations': self.generate_improvement_recommendations(evaluation),
            'detailed_results': results[:10],  # Первые 10 для примера
            'timestamp': datetime.datetime.now().isoformat()
        }
        
        return report

    def generate_improvement_recommendations(self, evaluation: Dict) -> List[str]:
        """Генерирует рекомендации по улучшению"""
        recommendations = []
        
        if evaluation['avg_confidence'] < 0.7:
            recommendations.append("Рассмотреть дообучение модели с дополнительными данными")
        
        if evaluation['low_confidence_ratio'] > 0.2:
            recommendations.append("Улучшить извлечение признаков для функций с низкой уверенностью")
        
        if self.training_accuracy < 0.85:
            recommendations.append("Добавить дополнительные правила категоризации")
        
        # Проверяем дисбаланс категорий
        category_counts = [stats['count'] for stats in evaluation['category_distribution'].values()]
        if max(category_counts) / min(category_counts) > 10:
            recommendations.append("Сбалансировать обучающую выборку по категориям")
        
        return recommendations

def main():
    """Главная функция для обучения и тестирования модели"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ML Categorization System')
    parser.add_argument('--api-data', required=True, help='Путь к файлу с данными API')
    parser.add_argument('--train', action='store_true', help='Обучить модель')
    parser.add_argument('--evaluate', action='store_true', help='Оценить качество')
    parser.add_argument('--output-report', help='Путь для сохранения отчета')
    
    args = parser.parse_args()
    
    # Создаем систему
    ml_system = MLCategorizationSystem()
    
    # Загружаем данные API
    with open(args.api_data, 'r', encoding='utf-8') as f:
        api_data = json.load(f)
    
    # Пытаемся загрузить существующие модели
    ml_system.load_models()
    
    if args.train:
        # Обучаем модель
        training_report = ml_system.train_model(api_data)
        print("📊 Отчет об обучении:")
        print(f"   Точность: {training_report['accuracy']:.3f}")
        print(f"   Образцов: {training_report['training_samples']}")
    
    if args.evaluate:
        # Собираем все функции для оценки
        all_functions = []
        for module_data in api_data.get('modules', {}).values():
            all_functions.extend(module_data.get('functions', []))
        
        # Генерируем отчет
        report = ml_system.generate_categorization_report(all_functions[:100])  # Первые 100
        
        print("📈 Отчет о категоризации:")
        print(f"   Функций обработано: {report['summary']['total_functions_categorized']}")
        print(f"   Средняя уверенность: {report['summary']['average_confidence']:.3f}")
        print(f"   Высокая уверенность: {report['summary']['high_confidence_predictions']:.1f}%")
        
        # Сохраняем отчет
        if args.output_report:
            with open(args.output_report, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            print(f"💾 Отчет сохранен: {args.output_report}")

if __name__ == '__main__':
    main() 