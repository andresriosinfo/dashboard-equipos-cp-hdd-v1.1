#!/usr/bin/env python
# coding: utf-8

import os
import logging
import time
import threading
import queue
import concurrent.futures
import pandas as pd
from typing import Dict, Any, Optional, Callable, List, Tuple
import traceback
import psutil
import gc

logger = logging.getLogger('hdd_data_analysis')

class BatchProcessor:
    """
    Handles batch processing of large DataFrames for HDD analysis.
    
    This class provides functionality to:
    1. Process DataFrames in smaller batches to manage memory
    2. Monitor memory usage and pause when necessary
    3. Handle batch processing errors gracefully
    4. Track processing statistics
    """
    
    def __init__(self, batch_size: int = 1000, max_workers: int = 4):
        """
        Initialize the batch processor.
        
        Args:
            batch_size: Size of each batch for processing
            max_workers: Maximum number of worker threads for parallel processing
        """
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.processing_stats = {
            'total_batches': 0,
            'total_records': 0,
            'successful_batches': 0,
            'failed_batches': 0,
            'total_processing_time': 0
        }
    
    def process_dataframe_in_batches(self, df: pd.DataFrame, process_func: Callable, 
                                   **kwargs) -> pd.DataFrame:
        """
        Process a DataFrame in batches to manage memory usage.
        
        Args:
            df: DataFrame to process
            process_func: Function to apply to each batch
            **kwargs: Additional arguments to pass to process_func
            
        Returns:
            Processed DataFrame
        """
        if df.empty:
            logger.warning("DataFrame is empty, nothing to process")
            return df
        
        start_time = time.time()
        total_rows = len(df)
        batch_count = (total_rows + self.batch_size - 1) // self.batch_size
        
        logger.info(f"Processing DataFrame with {total_rows} rows in {batch_count} batches")
        
        processed_batches = []
        self.processing_stats['total_batches'] = batch_count
        self.processing_stats['total_records'] = total_rows
        
        for i in range(batch_count):
            batch_start = i * self.batch_size
            batch_end = min((i + 1) * self.batch_size, total_rows)
            
            # Check memory usage before processing each batch
            memory_percent = psutil.virtual_memory().percent
            if memory_percent > 85:
                logger.warning(f"Memory usage is high ({memory_percent:.1f}%), pausing for 2 seconds")
                time.sleep(2)
                # Force garbage collection
                gc.collect()
            
            # Create batch with minimal memory footprint
            batch_df = df.iloc[batch_start:batch_end].copy()
            
            try:
                logger.debug(f"Processing batch {i+1}/{batch_count} (rows {batch_start}:{batch_end})")
                
                # Process the batch
                processed_batch = process_func(batch_df, **kwargs)
                
                if processed_batch is not None and not processed_batch.empty:
                    processed_batches.append(processed_batch)
                    self.processing_stats['successful_batches'] += 1
                    logger.debug(f"Batch {i+1} processed successfully: {len(processed_batch)} records")
                else:
                    logger.warning(f"Batch {i+1} returned empty or None result")
                    self.processing_stats['failed_batches'] += 1
                
                # Clear batch DataFrame to free memory
                del batch_df
                gc.collect()
                    
            except Exception as e:
                logger.error(f"Error processing batch {i+1}: {str(e)}")
                logger.error(traceback.format_exc())
                self.processing_stats['failed_batches'] += 1
                # Clear batch DataFrame even if there was an error
                del batch_df
                gc.collect()
                continue
        
        # Combine all processed batches
        if processed_batches:
            result_df = pd.concat(processed_batches, ignore_index=True)
            logger.info(f"Batch processing completed: {len(result_df)} records processed successfully")
        else:
            result_df = pd.DataFrame()
            logger.warning("No batches were processed successfully")
        
        # Clear processed batches to free memory
        del processed_batches
        gc.collect()
        
        # Update processing statistics
        self.processing_stats['total_processing_time'] = time.time() - start_time
        
        logger.info(f"Batch processing stats: {self.processing_stats}")
        
        return result_df
    
    def process_dataframe_parallel(self, df: pd.DataFrame, process_func: Callable, 
                                 **kwargs) -> pd.DataFrame:
        """
        Process a DataFrame in parallel using multiple threads.
        
        Args:
            df: DataFrame to process
            process_func: Function to apply to each batch
            **kwargs: Additional arguments to pass to process_func
            
        Returns:
            Processed DataFrame
        """
        if df.empty:
            logger.warning("DataFrame is empty, nothing to process")
            return df
        
        start_time = time.time()
        total_rows = len(df)
        batch_count = (total_rows + self.batch_size - 1) // self.batch_size
        
        logger.info(f"Processing {total_rows} records in {batch_count} batches using {self.max_workers} workers")
        
        # Create batches
        batches = []
        for i in range(batch_count):
            batch_start = i * self.batch_size
            batch_end = min((i + 1) * self.batch_size, total_rows)
            batch_df = df.iloc[batch_start:batch_end].copy()
            batches.append((i, batch_df))
        
        # Process batches in parallel
        processed_batches = []
        self.processing_stats['total_batches'] = batch_count
        self.processing_stats['total_records'] = total_rows
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all batch processing tasks
            future_to_batch = {
                executor.submit(self._process_batch, batch_idx, batch_df, process_func, **kwargs): batch_idx
                for batch_idx, batch_df in batches
            }
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_batch):
                batch_idx = future_to_batch[future]
                
                try:
                    result = future.result()
                    if result is not None and not result.empty:
                        processed_batches.append(result)
                        self.processing_stats['successful_batches'] += 1
                        logger.debug(f"Batch {batch_idx+1} processed successfully: {len(result)} records")
                    else:
                        logger.warning(f"Batch {batch_idx+1} returned empty or None result")
                        self.processing_stats['failed_batches'] += 1
                        
                except Exception as e:
                    logger.error(f"Error processing batch {batch_idx+1}: {str(e)}")
                    self.processing_stats['failed_batches'] += 1
        
        # Combine all processed batches
        if processed_batches:
            result_df = pd.concat(processed_batches, ignore_index=True)
            logger.info(f"Parallel processing completed: {len(result_df)} records processed successfully")
        else:
            result_df = pd.DataFrame()
            logger.warning("No batches were processed successfully")
        
        # Update processing statistics
        self.processing_stats['total_execution_time'] = time.time() - start_time
        
        logger.info(f"Parallel processing stats: {self.processing_stats}")
        
        return result_df
    
    def _process_batch(self, batch_idx: int, batch_df: pd.DataFrame, 
                      process_func: Callable, **kwargs) -> Optional[pd.DataFrame]:
        """
        Process a single batch.
        
        Args:
            batch_idx: Index of the batch
            batch_df: DataFrame containing the batch data
            process_func: Function to apply to the batch
            **kwargs: Additional arguments to pass to process_func
            
        Returns:
            Processed batch DataFrame or None if error
        """
        try:
            return process_func(batch_df, **kwargs)
        except Exception as e:
            logger.error(f"Error in batch {batch_idx}: {str(e)}")
            return None
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get current processing statistics."""
        return self.processing_stats.copy()
    
    def reset_stats(self):
        """Reset processing statistics."""
        self.processing_stats = {
            'total_batches': 0,
            'total_records': 0,
            'successful_batches': 0,
            'failed_batches': 0,
            'total_processing_time': 0
        }


class ParallelProcessor:
    """
    Handles parallel execution of multiple tasks for HDD analysis.
    
    This class provides functionality to:
    1. Execute multiple functions in parallel
    2. Manage task dependencies
    3. Handle task failures gracefully
    4. Monitor execution progress
    """
    
    def __init__(self, max_workers: int = 4):
        """
        Initialize the parallel processor.
        
        Args:
            max_workers: Maximum number of worker threads
        """
        self.max_workers = max_workers
        self.execution_stats = {
            'total_tasks': 0,
            'completed_tasks': 0,
            'failed_tasks': 0,
            'total_execution_time': 0
        }
    
    def execute_parallel(self, tasks: List[Tuple[Callable, Tuple, Dict]]) -> List[Any]:
        """
        Execute multiple tasks in parallel.
        
        Args:
            tasks: List of tuples containing (function, args, kwargs)
            
        Returns:
            List of results from each task
        """
        if not tasks:
            logger.warning("No tasks to execute")
            return []
        
        start_time = time.time()
        results = []
        
        self.execution_stats['total_tasks'] = len(tasks)
        self.execution_stats['completed_tasks'] = 0
        self.execution_stats['failed_tasks'] = 0
        
        logger.info(f"Executing {len(tasks)} tasks in parallel using {self.max_workers} workers")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_task = {
                executor.submit(func, *args, **kwargs): i
                for i, (func, args, kwargs) in enumerate(tasks)
            }
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_task):
                task_idx = future_to_task[future]
                
                try:
                    result = future.result()
                    results.append(result)
                    self.execution_stats['completed_tasks'] += 1
                    logger.debug(f"Task {task_idx+1} completed successfully")
                    
                except Exception as e:
                    logger.error(f"Error in task {task_idx+1}: {str(e)}")
                    logger.error(traceback.format_exc())
                    results.append(None)
                    self.execution_stats['failed_tasks'] += 1
        
        # Update execution statistics
        self.execution_stats['total_execution_time'] = time.time() - start_time
        
        logger.info(f"Parallel execution completed: {self.execution_stats['completed_tasks']} successful, {self.execution_stats['failed_tasks']} failed")
        logger.info(f"Parallel execution stats: {self.execution_stats}")
        
        return results
    
    def execute_with_dependencies(self, tasks: List[Tuple[Callable, Tuple, Dict, List[int]]]) -> List[Any]:
        """
        Execute tasks with dependencies in parallel.
        
        Args:
            tasks: List of tuples containing (function, args, kwargs, dependencies)
                  where dependencies is a list of task indices that must complete first
            
        Returns:
            List of results from each task
        """
        if not tasks:
            logger.warning("No tasks to execute")
            return []
        
        start_time = time.time()
        results = [None] * len(tasks)
        
        self.execution_stats['total_tasks'] = len(tasks)
        self.execution_stats['completed_tasks'] = 0
        self.execution_stats['failed_tasks'] = 0
        
        logger.info(f"Executing {len(tasks)} tasks with dependencies using {self.max_workers} workers")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_task = {}
            completed_tasks = set()
            
            # Submit initial tasks with no dependencies
            for i, (func, args, kwargs, dependencies) in enumerate(tasks):
                if not dependencies:
                    future = executor.submit(func, *args, **kwargs)
                    future_to_task[future] = i
                    logger.debug(f"Submitted initial task {i+1}")
            
            # Process completed tasks and submit dependent tasks
            while future_to_task:
                # Wait for any task to complete
                done, not_done = concurrent.futures.wait(
                    future_to_task.keys(), 
                    return_when=concurrent.futures.FIRST_COMPLETED
                )
                
                # Process completed tasks
                for future in done:
                    task_idx = future_to_task[future]
                    
                    try:
                        result = future.result()
                        results[task_idx] = result
                        completed_tasks.add(task_idx)
                        self.execution_stats['completed_tasks'] += 1
                        logger.debug(f"Task {task_idx+1} completed successfully")
                        
                    except Exception as e:
                        logger.error(f"Error in task {task_idx+1}: {str(e)}")
                        logger.error(traceback.format_exc())
                        results[task_idx] = None
                        self.execution_stats['failed_tasks'] += 1
                    
                    # Remove from active tasks
                    del future_to_task[future]
                
                # Submit new tasks whose dependencies are now satisfied
                for i, (func, args, kwargs, dependencies) in enumerate(tasks):
                    if i not in completed_tasks and i not in future_to_task:
                        if all(dep in completed_tasks for dep in dependencies):
                            future = executor.submit(func, *args, **kwargs)
                            future_to_task[future] = i
                            logger.debug(f"Submitted dependent task {i+1}")
        
        # Update execution statistics
        self.execution_stats['total_execution_time'] = time.time() - start_time
        
        logger.info(f"Dependency execution completed: {self.execution_stats['completed_tasks']} successful, {self.execution_stats['failed_tasks']} failed")
        logger.info(f"Dependency execution stats: {self.execution_stats}")
        
        return results
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get current execution statistics."""
        return self.execution_stats.copy()
    
    def reset_stats(self):
        """Reset execution statistics."""
        self.execution_stats = {
            'total_tasks': 0,
            'completed_tasks': 0,
            'failed_tasks': 0,
            'total_execution_time': 0
        }


# Global instances
_batch_processor = None
_parallel_processor = None

def get_batch_processor(batch_size: int = None, max_workers: int = None) -> BatchProcessor:
    """
    Get or create a batch processor instance.
    
    Args:
        batch_size: Size of batches (optional, will use default if not provided)
        max_workers: Maximum number of workers (optional, will use default if not provided)
        
    Returns:
        BatchProcessor instance
    """
    global _batch_processor
    
    if _batch_processor is None:
        # Get configuration values
        from hdd_config_manager import get_config
        
        if batch_size is None:
            batch_size = get_config('tamano_lote', 1000)
        if max_workers is None:
            max_workers = get_config('max_hilos', 4)
        
        _batch_processor = BatchProcessor(batch_size=batch_size, max_workers=max_workers)
        logger.info(f"Created batch processor with batch_size={batch_size}, max_workers={max_workers}")
    
    return _batch_processor

def get_parallel_processor(max_workers: int = None) -> ParallelProcessor:
    """
    Get or create a parallel processor instance.
    
    Args:
        max_workers: Maximum number of workers (optional, will use default if not provided)
        
    Returns:
        ParallelProcessor instance
    """
    global _parallel_processor
    
    if _parallel_processor is None:
        # Get configuration values
        from hdd_config_manager import get_config
        
        if max_workers is None:
            max_workers = get_config('max_hilos', 4)
        
        _parallel_processor = ParallelProcessor(max_workers=max_workers)
        logger.info(f"Created parallel processor with max_workers={max_workers}")
    
    return _parallel_processor 