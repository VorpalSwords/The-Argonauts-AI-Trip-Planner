"""
Agent Evaluation System - Capstone Feature

This module evaluates the trip planner agent system on multiple dimensions:
- Performance (speed, efficiency)
- Quality (itinerary completeness, feasibility)
- User satisfaction (matches preferences, interests)
- Technical excellence (tool usage, architecture)

Part of the capstone project evaluation requirements.
"""

from typing import Dict, Any
from src.models.trip_models import TripInput, TripItinerary
from datetime import datetime


class TripPlannerEvaluator:
    """
    Evaluation system for Trip Planner Agent.
    
    Implements multi-dimensional evaluation:
    1. Performance Metrics
    2. Quality Assessment
    3. Feature Coverage
    4. User Satisfaction Proxy
    """
    
    def __init__(self):
        self.evaluation_criteria = {
            "performance": {
                "research_speed": 30,  # Target seconds
                "planning_speed": 30,
                "total_time": 120,
                "max_review_iterations": 3
            },
            "quality": {
                "min_attractions": 5,
                "min_activities_per_day": 2,
                "budget_accuracy": 0.2,  # 20% tolerance
                "itinerary_completeness": 0.9  # 90% complete
            },
            "features": [
                "google_search",
                "code_execution",
                "sessions",
                "memory",
                "observability",
                "sequential_agents",
                "loop_agent"
            ]
        }
    
    def evaluate(
        self,
        trip_input: TripInput,
        itinerary: TripItinerary,
        metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Comprehensive evaluation of agent performance.
        
        Args:
            trip_input: Original trip request
            itinerary: Generated itinerary
            metrics: Performance metrics from orchestrator
            
        Returns:
            Evaluation results with scores and analysis
        """
        evaluation = {
            "timestamp": datetime.now().isoformat(),
            "trip_destination": trip_input.destination,
            "scores": {},
            "details": {},
            "recommendations": []
        }
        
        # 1. Performance Evaluation
        perf_score = self._evaluate_performance(metrics)
        evaluation["scores"]["performance"] = perf_score
        evaluation["details"]["performance"] = {
            "research_time": metrics.get("research_time", 0),
            "planning_time": metrics.get("planning_time", 0),
            "total_time": metrics.get("total_time", 0),
            "review_iterations": metrics.get("review_iterations", 0)
        }
        
        # 2. Quality Evaluation
        quality_score = self._evaluate_quality(trip_input, itinerary)
        evaluation["scores"]["quality"] = quality_score
        evaluation["details"]["quality"] = {
            "num_day_plans": len(itinerary.day_plans),
            "budget": itinerary.total_estimated_cost,
            "packing_list_items": len(itinerary.packing_list),
            "important_notes": len(itinerary.important_notes)
        }
        
        # 3. Feature Coverage
        feature_score = self._evaluate_features(metrics)
        evaluation["scores"]["feature_coverage"] = feature_score
        evaluation["details"]["features_used"] = metrics.get("features_used", [])
        
        # 4. User Satisfaction Proxy
        satisfaction_score = self._evaluate_satisfaction(trip_input, itinerary)
        evaluation["scores"]["user_satisfaction"] = satisfaction_score
        
        # Calculate overall score
        weights = {
            "performance": 0.2,
            "quality": 0.4,
            "feature_coverage": 0.2,
            "user_satisfaction": 0.2
        }
        
        overall = sum(
            evaluation["scores"][key] * weights[key]
            for key in weights
        )
        evaluation["overall_score"] = round(overall, 2)
        evaluation["grade"] = self._get_grade(overall)
        
        # Generate recommendations
        evaluation["recommendations"] = self._generate_recommendations(evaluation)
        
        return evaluation
    
    def _evaluate_performance(self, metrics: Dict[str, Any]) -> float:
        """Evaluate performance metrics (0-10 scale)"""
        criteria = self.evaluation_criteria["performance"]
        
        # Research speed
        research_score = min(10, (criteria["research_speed"] / max(metrics.get("research_time", 1), 1)) * 10)
        
        # Planning speed
        planning_score = min(10, (criteria["planning_speed"] / max(metrics.get("planning_time", 1), 1)) * 10)
        
        # Total time
        total_score = min(10, (criteria["total_time"] / max(metrics.get("total_time", 1), 1)) * 10)
        
        # Iterations efficiency
        iterations = metrics.get("review_iterations", 1)
        iteration_score = 10 - (iterations - 1) * 2  # Penalty for more iterations
        
        # Average
        perf_score = (research_score + planning_score + total_score + iteration_score) / 4
        return round(min(10, max(0, perf_score)), 2)
    
    def _evaluate_quality(self, trip_input: TripInput, itinerary: TripItinerary) -> float:
        """Evaluate itinerary quality (0-10 scale)"""
        scores = []
        
        # 1. Completeness (all days planned)
        if itinerary.duration_days == len(itinerary.day_plans):
            scores.append(10)
        else:
            scores.append((len(itinerary.day_plans) / itinerary.duration_days) * 10)
        
        # 2. Activity richness
        total_activities = sum(
            len(day.morning_activities) + len(day.afternoon_activities) + len(day.evening_activities)
            for day in itinerary.day_plans
        )
        avg_activities = total_activities / max(len(itinerary.day_plans), 1)
        activity_score = min(10, avg_activities * 2)  # Target 5 activities/day
        scores.append(activity_score)
        
        # 3. Budget reasonableness
        daily_budget = itinerary.total_estimated_cost / max(itinerary.duration_days, 1)
        budget_levels = {"budget": 100, "mid-range": 200, "luxury": 400}
        expected = budget_levels.get(trip_input.preferences.budget_level, 200)
        budget_diff = abs(daily_budget - expected) / expected
        budget_score = max(0, 10 - (budget_diff * 10))
        scores.append(budget_score)
        
        # 4. Practical details (packing list, notes)
        details_score = min(10, (len(itinerary.packing_list) + len(itinerary.important_notes)) / 2)
        scores.append(details_score)
        
        return round(sum(scores) / len(scores), 2)
    
    def _evaluate_features(self, metrics: Dict[str, Any]) -> float:
        """Evaluate ADK feature usage (0-10 scale)"""
        required_features = self.evaluation_criteria["features"]
        features_used = metrics.get("features_used", [])
        
        # Count how many required features were used
        used_count = sum(
            1 for feature in required_features
            if any(feature.lower() in str(used).lower() for used in features_used)
        )
        
        # Score based on coverage
        coverage = used_count / len(required_features)
        return round(coverage * 10, 2)
    
    def _evaluate_satisfaction(self, trip_input: TripInput, itinerary: TripItinerary) -> float:
        """Evaluate user satisfaction proxy (0-10 scale)"""
        scores = []
        
        # 1. Duration match
        if itinerary.duration_days == trip_input.dates.duration_days:
            scores.append(10)
        else:
            scores.append(5)
        
        # 2. Destination match
        if trip_input.destination.lower() in itinerary.destination.lower():
            scores.append(10)
        else:
            scores.append(5)
        
        # 3. Has generated content
        if len(itinerary.generated_itinerary) > 100:
            scores.append(10)
        else:
            scores.append(5)
        
        # 4. All days have plans
        if all(
            day.morning_activities and day.afternoon_activities
            for day in itinerary.day_plans
        ):
            scores.append(10)
        else:
            scores.append(7)
        
        return round(sum(scores) / len(scores), 2)
    
    def _get_grade(self, score: float) -> str:
        """Convert score to letter grade"""
        if score >= 9.0:
            return "A+ (Excellent)"
        elif score >= 8.0:
            return "A (Very Good)"
        elif score >= 7.0:
            return "B (Good)"
        elif score >= 6.0:
            return "C (Acceptable)"
        else:
            return "D (Needs Improvement)"
    
    def _generate_recommendations(self, evaluation: Dict[str, Any]) -> list:
        """Generate improvement recommendations"""
        recommendations = []
        
        scores = evaluation["scores"]
        
        if scores.get("performance", 10) < 7:
            recommendations.append(
                "Consider caching research results or using faster models for improved performance."
            )
        
        if scores.get("quality", 10) < 7:
            recommendations.append(
                "Improve itinerary quality by adding more detailed activities and practical information."
            )
        
        if scores.get("feature_coverage", 10) < 7:
            recommendations.append(
                "Utilize more ADK features like code_execution, memory persistence, and observability."
            )
        
        if scores.get("user_satisfaction", 10) < 8:
            recommendations.append(
                "Enhance user satisfaction by better matching preferences and providing richer content."
            )
        
        if not recommendations:
            recommendations.append("Excellent work! All metrics are strong. Consider adding deployment.")
        
        return recommendations


# Convenience function
def evaluate_agent(trip_input: TripInput, itinerary: TripItinerary, metrics: dict) -> dict:
    """Standalone evaluation function"""
    evaluator = TripPlannerEvaluator()
    return evaluator.evaluate(trip_input, itinerary, metrics)

